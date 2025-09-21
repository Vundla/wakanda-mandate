from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
from ..core.database import get_db
from ..core.auth import get_current_user
from ..users.models import User
from .models import ChatSession, ChatMessage, AIAnalysis, AIWorkflow, WorkflowExecution
from .schemas import (
    ChatSessionCreate, ChatSessionResponse, ChatSessionUpdate,
    ChatMessageResponse, ChatRequest, ChatResponse,
    AIAnalysisCreate, AIAnalysisResponse,
    AIWorkflowCreate, AIWorkflowResponse, AIWorkflowUpdate,
    WorkflowExecutionCreate, WorkflowExecutionResponse,
    AIStats, DocumentAnalysisRequest, DocumentAnalysisResponse,
    RecommendationRequest, RecommendationResponse
)
from .openrouter import (
    OpenRouterClient, calculate_cost, extract_tokens_from_response,
    build_government_system_prompt, build_analysis_prompt, build_recommendation_prompt
)

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Chat with AI using OpenRouter"""
    try:
        openrouter = OpenRouterClient()
        
        # Get or create chat session
        if chat_request.session_id:
            session = db.query(ChatSession).filter(
                ChatSession.id == chat_request.session_id,
                ChatSession.user_id == current_user.id
            ).first()
            if not session:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Chat session not found"
                )
        else:
            # Create new session
            session = ChatSession(
                user_id=current_user.id,
                title=f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                model=chat_request.model,
                system_prompt=chat_request.system_prompt or build_government_system_prompt()
            )
            db.add(session)
            db.commit()
            db.refresh(session)
        
        # Get conversation history
        messages = db.query(ChatMessage).filter(
            ChatMessage.session_id == session.id
        ).order_by(ChatMessage.created_at).all()
        
        # Build message list for API
        api_messages = []
        if session.system_prompt:
            api_messages.append({"role": "system", "content": session.system_prompt})
        
        for msg in messages:
            api_messages.append({"role": msg.role, "content": msg.content})
        
        # Add new user message
        api_messages.append({"role": "user", "content": chat_request.message})
        
        # Get AI response
        response = await openrouter.chat_completion(
            messages=api_messages,
            model=chat_request.model
        )
        
        ai_content = response["choices"][0]["message"]["content"]
        tokens_used = extract_tokens_from_response(response)
        cost = calculate_cost(tokens_used, chat_request.model)
        
        # Save user message
        user_message = ChatMessage(
            session_id=session.id,
            role="user",
            content=chat_request.message
        )
        db.add(user_message)
        
        # Save AI response
        ai_message = ChatMessage(
            session_id=session.id,
            role="assistant",
            content=ai_content,
            tokens_used=tokens_used,
            cost=cost,
            model=chat_request.model
        )
        db.add(ai_message)
        
        db.commit()
        
        return ChatResponse(
            session_id=session.id,
            response=ai_content,
            tokens_used=tokens_used,
            cost=cost,
            model=chat_request.model
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI chat error: {str(e)}"
        )


@router.post("/chat/sessions", response_model=ChatSessionResponse)
def create_chat_session(
    session: ChatSessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new chat session"""
    db_session = ChatSession(
        **session.dict(),
        user_id=current_user.id,
        system_prompt=session.system_prompt or build_government_system_prompt()
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session


@router.get("/chat/sessions", response_model=List[ChatSessionResponse])
def get_chat_sessions(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's chat sessions"""
    sessions = db.query(ChatSession).filter(
        ChatSession.user_id == current_user.id,
        ChatSession.is_active == True
    ).order_by(desc(ChatSession.updated_at)).offset(skip).limit(limit).all()
    return sessions


@router.get("/chat/sessions/{session_id}/messages", response_model=List[ChatMessageResponse])
def get_chat_messages(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get messages from a chat session"""
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.created_at).all()
    
    return messages


@router.post("/analyze/document", response_model=DocumentAnalysisResponse)
async def analyze_document(
    request: DocumentAnalysisRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze document content using AI"""
    if current_user.role not in ["admin", "government_official"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    try:
        openrouter = OpenRouterClient()
        
        # Build analysis prompt
        messages = build_analysis_prompt(
            request.analysis_type,
            request.document_content,
            request.custom_instructions
        )
        
        # Get AI analysis
        response = await openrouter.chat_completion(
            messages=messages,
            model="openai/gpt-4"
        )
        
        analysis_result = response["choices"][0]["message"]["content"]
        tokens_used = extract_tokens_from_response(response)
        cost = calculate_cost(tokens_used, "openai/gpt-4")
        
        # Save analysis
        db_analysis = AIAnalysis(
            analysis_type=request.analysis_type,
            input_data=request.document_content,
            analysis_result=analysis_result,
            model="openai/gpt-4",
            tokens_used=tokens_used,
            cost=cost,
            requested_by=current_user.id
        )
        
        db.add(db_analysis)
        db.commit()
        db.refresh(db_analysis)
        
        # Parse response for structured data
        response_data = DocumentAnalysisResponse(
            analysis_id=db_analysis.id,
            summary=analysis_result if request.analysis_type == "summary" else None,
            confidence_score=0.85  # Simplified confidence score
        )
        
        # Try to extract structured information based on analysis type
        if request.analysis_type == "extraction":
            try:
                # Simple extraction of key points
                lines = analysis_result.split('\n')
                key_points = [line.strip('- ') for line in lines if line.strip().startswith('- ')]
                response_data.key_points = key_points[:10]  # Limit to 10 points
            except:
                pass
        
        return response_data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document analysis error: {str(e)}"
        )


@router.post("/recommend", response_model=RecommendationResponse)
async def get_recommendations(
    request: RecommendationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AI-powered recommendations"""
    if current_user.role not in ["admin", "government_official"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    try:
        openrouter = OpenRouterClient()
        
        # Build recommendation prompt
        messages = build_recommendation_prompt(
            request.context,
            request.request_type,
            request.parameters
        )
        
        # Get AI recommendations
        response = await openrouter.chat_completion(
            messages=messages,
            model="openai/gpt-4"
        )
        
        recommendations_text = response["choices"][0]["message"]["content"]
        tokens_used = extract_tokens_from_response(response)
        cost = calculate_cost(tokens_used, "openai/gpt-4")
        
        # Save analysis
        db_analysis = AIAnalysis(
            analysis_type="recommendation",
            input_data=json.dumps({
                "context": request.context,
                "request_type": request.request_type,
                "parameters": request.parameters
            }),
            analysis_result=recommendations_text,
            model="openai/gpt-4",
            tokens_used=tokens_used,
            cost=cost,
            requested_by=current_user.id
        )
        
        db.add(db_analysis)
        db.commit()
        
        # Parse recommendations (simplified)
        recommendations = [
            {
                "title": f"Recommendation for {request.request_type}",
                "description": recommendations_text,
                "priority": "high",
                "category": request.request_type
            }
        ]
        
        return RecommendationResponse(
            recommendations=recommendations,
            reasoning=recommendations_text,
            confidence_score=0.85,
            implementation_steps=["Review recommendations", "Consult stakeholders", "Develop implementation plan"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Recommendation error: {str(e)}"
        )


@router.get("/stats", response_model=AIStats)
def get_ai_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get AI usage statistics"""
    if current_user.role not in ["admin", "government_official"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    total_sessions = db.query(ChatSession).count()
    total_messages = db.query(ChatMessage).count()
    total_analyses = db.query(AIAnalysis).count()
    total_workflows = db.query(AIWorkflow).count()
    total_executions = db.query(WorkflowExecution).count()
    
    # Token and cost statistics
    total_tokens = db.query(func.sum(ChatMessage.tokens_used)).scalar() or 0
    message_cost = db.query(func.sum(ChatMessage.cost)).scalar() or 0
    analysis_cost = db.query(func.sum(AIAnalysis.cost)).scalar() or 0
    total_cost = message_cost + analysis_cost
    
    # Popular models
    model_usage = db.query(
        ChatMessage.model, func.count(ChatMessage.id)
    ).group_by(ChatMessage.model).all()
    popular_models = {model: count for model, count in model_usage if model}
    
    # Usage by type
    analysis_types = db.query(
        AIAnalysis.analysis_type, func.count(AIAnalysis.id)
    ).group_by(AIAnalysis.analysis_type).all()
    usage_by_type = {analysis_type: count for analysis_type, count in analysis_types}
    
    return AIStats(
        total_chat_sessions=total_sessions,
        total_messages=total_messages,
        total_analyses=total_analyses,
        total_workflows=total_workflows,
        total_executions=total_executions,
        total_tokens_used=total_tokens,
        total_cost=total_cost,
        popular_models=popular_models,
        usage_by_type=usage_by_type
    )


@router.get("/models")
async def get_available_models():
    """Get available AI models from OpenRouter"""
    try:
        openrouter = OpenRouterClient()
        models = await openrouter.get_models()
        
        # Filter for common government use models
        filtered_models = [
            model for model in models
            if any(provider in model.get("id", "") for provider in ["openai", "anthropic", "meta-llama"])
        ]
        
        return {"models": filtered_models}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching models: {str(e)}"
        )