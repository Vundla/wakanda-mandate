from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class ChatSessionBase(BaseModel):
    title: str
    model: str = "openai/gpt-3.5-turbo"
    system_prompt: Optional[str] = None


class ChatSessionCreate(ChatSessionBase):
    pass


class ChatSessionUpdate(BaseModel):
    title: Optional[str] = None
    system_prompt: Optional[str] = None
    is_active: Optional[bool] = None


class ChatSessionResponse(ChatSessionBase):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ChatMessageBase(BaseModel):
    content: str


class ChatMessageCreate(ChatMessageBase):
    pass


class ChatMessageResponse(ChatMessageBase):
    id: int
    session_id: int
    role: str
    tokens_used: Optional[int] = None
    cost: Optional[float] = None
    model: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[int] = None
    model: Optional[str] = "openai/gpt-3.5-turbo"
    system_prompt: Optional[str] = None


class ChatResponse(BaseModel):
    session_id: int
    response: str
    tokens_used: Optional[int] = None
    cost: Optional[float] = None
    model: str


class AIAnalysisBase(BaseModel):
    analysis_type: str
    input_data: str
    model: str = "openai/gpt-4"


class AIAnalysisCreate(AIAnalysisBase):
    pass


class AIAnalysisResponse(AIAnalysisBase):
    id: int
    analysis_result: str
    confidence_score: Optional[float] = None
    tokens_used: Optional[int] = None
    cost: Optional[float] = None
    requested_by: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class AIWorkflowBase(BaseModel):
    name: str
    description: str
    workflow_type: str
    input_schema: str
    prompt_template: str
    model: str = "openai/gpt-3.5-turbo"


class AIWorkflowCreate(AIWorkflowBase):
    pass


class AIWorkflowUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    input_schema: Optional[str] = None
    prompt_template: Optional[str] = None
    model: Optional[str] = None
    is_active: Optional[bool] = None


class AIWorkflowResponse(AIWorkflowBase):
    id: int
    is_active: bool
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class WorkflowExecutionBase(BaseModel):
    input_data: str


class WorkflowExecutionCreate(WorkflowExecutionBase):
    workflow_id: int


class WorkflowExecutionResponse(WorkflowExecutionBase):
    id: int
    workflow_id: int
    output_data: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    tokens_used: Optional[int] = None
    cost: Optional[float] = None
    executed_by: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class AIStats(BaseModel):
    total_chat_sessions: int
    total_messages: int
    total_analyses: int
    total_workflows: int
    total_executions: int
    total_tokens_used: int
    total_cost: float
    popular_models: Dict[str, int]
    usage_by_type: Dict[str, int]


class DocumentAnalysisRequest(BaseModel):
    document_content: str
    analysis_type: str = "summary"  # summary, sentiment, extraction, classification
    custom_instructions: Optional[str] = None


class DocumentAnalysisResponse(BaseModel):
    analysis_id: int
    summary: Optional[str] = None
    key_points: Optional[List[str]] = None
    sentiment: Optional[str] = None
    entities: Optional[List[Dict[str, Any]]] = None
    classification: Optional[str] = None
    confidence_score: Optional[float] = None


class RecommendationRequest(BaseModel):
    context: str
    request_type: str  # policy, budget, efficiency, etc.
    parameters: Optional[Dict[str, Any]] = None


class RecommendationResponse(BaseModel):
    recommendations: List[Dict[str, Any]]
    reasoning: str
    confidence_score: float
    implementation_steps: Optional[List[str]] = None