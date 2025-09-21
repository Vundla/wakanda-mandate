from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_, desc, text
from typing import List, Optional
from datetime import datetime, timedelta
from ..core.database import get_db
from ..core.auth import get_current_user
from ..users.models import User
from .models import PolicyDocument, PolicyAmendment, PolicyComment, PolicyCitation, PolicyAnalytics
from .schemas import (
    PolicyDocumentCreate, PolicyDocumentResponse, PolicyDocumentUpdate,
    PolicyAmendmentCreate, PolicyAmendmentResponse,
    PolicyCommentCreate, PolicyCommentResponse,
    PolicySearchFilters, PolicySearchResult, PolicyStats,
    PolicyAnalyticsReport, PolicyRecommendation, PolicyImpactAnalysis,
    CitationNetwork
)

router = APIRouter(prefix="/policy", tags=["policy"])


@router.post("/documents", response_model=PolicyDocumentResponse)
def create_policy_document(
    document: PolicyDocumentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new policy document"""
    if current_user.role not in ["admin", "government_official"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Check if document number already exists
    existing = db.query(PolicyDocument).filter(
        PolicyDocument.document_number == document.document_number
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document number already exists"
        )
    
    db_document = PolicyDocument(**document.dict(), created_by=current_user.id)
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document


@router.get("/documents/search", response_model=List[PolicySearchResult])
def search_policy_documents(
    query: str = Query(..., description="Search query"),
    skip: int = 0,
    limit: int = 100,
    document_type: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    status: Optional[str] = Query("active"),
    db: Session = Depends(get_db)
):
    """Advanced policy document search with full-text search capabilities"""
    
    # Build base query for public documents or authenticated users
    base_query = db.query(PolicyDocument).filter(PolicyDocument.is_public == True)
    
    # Apply status filter
    if status:
        base_query = base_query.filter(PolicyDocument.status == status)
    
    # Apply categorical filters
    if document_type:
        base_query = base_query.filter(PolicyDocument.document_type == document_type)
    
    if category:
        base_query = base_query.filter(PolicyDocument.category == category)
    
    if department:
        base_query = base_query.filter(PolicyDocument.department == department)
    
    # Full-text search across multiple fields
    search_query = base_query.filter(
        or_(
            PolicyDocument.title.ilike(f"%{query}%"),
            PolicyDocument.summary.ilike(f"%{query}%"),
            PolicyDocument.content.ilike(f"%{query}%"),
            PolicyDocument.keywords.ilike(f"%{query}%"),
            PolicyDocument.document_number.ilike(f"%{query}%")
        )
    )
    
    # Order by relevance (simplified - title matches first, then summary, then content)
    # In production, consider using full-text search engines like Elasticsearch
    title_matches = search_query.filter(PolicyDocument.title.ilike(f"%{query}%"))
    summary_matches = search_query.filter(
        PolicyDocument.summary.ilike(f"%{query}%"),
        ~PolicyDocument.title.ilike(f"%{query}%")
    )
    content_matches = search_query.filter(
        PolicyDocument.content.ilike(f"%{query}%"),
        ~PolicyDocument.title.ilike(f"%{query}%"),
        ~PolicyDocument.summary.ilike(f"%{query}%")
    )
    
    # Combine results with relevance scoring
    results = []
    
    # Title matches (highest relevance)
    for doc in title_matches.offset(skip).limit(limit).all():
        result = PolicySearchResult(
            id=doc.id,
            title=doc.title,
            document_number=doc.document_number,
            document_type=doc.document_type,
            category=doc.category,
            department=doc.department,
            summary=doc.summary,
            effective_date=doc.effective_date,
            status=doc.status,
            relevance_score=1.0
        )
        results.append(result)
    
    # Add summary matches if we have room
    remaining_limit = limit - len(results)
    if remaining_limit > 0:
        for doc in summary_matches.limit(remaining_limit).all():
            result = PolicySearchResult(
                id=doc.id,
                title=doc.title,
                document_number=doc.document_number,
                document_type=doc.document_type,
                category=doc.category,
                department=doc.department,
                summary=doc.summary,
                effective_date=doc.effective_date,
                status=doc.status,
                relevance_score=0.7
            )
            results.append(result)
    
    # Add content matches if we still have room
    remaining_limit = limit - len(results)
    if remaining_limit > 0:
        for doc in content_matches.limit(remaining_limit).all():
            result = PolicySearchResult(
                id=doc.id,
                title=doc.title,
                document_number=doc.document_number,
                document_type=doc.document_type,
                category=doc.category,
                department=doc.department,
                summary=doc.summary,
                effective_date=doc.effective_date,
                status=doc.status,
                relevance_score=0.5
            )
            results.append(result)
    
    # Update search appearances for analytics
    for result in results:
        # Update or create analytics record
        today = datetime.now().date()
        analytics = db.query(PolicyAnalytics).filter(
            PolicyAnalytics.policy_document_id == result.id,
            func.date(PolicyAnalytics.analytics_date) == today
        ).first()
        
        if analytics:
            analytics.search_appearances += 1
        else:
            analytics = PolicyAnalytics(
                policy_document_id=result.id,
                analytics_date=datetime.now(),
                search_appearances=1
            )
            db.add(analytics)
    
    db.commit()
    return results


@router.get("/documents", response_model=List[PolicyDocumentResponse])
def get_policy_documents(
    skip: int = 0,
    limit: int = 100,
    document_type: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    is_public: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    """Get policy documents with filtering"""
    query = db.query(PolicyDocument)
    
    # Apply filters
    if document_type:
        query = query.filter(PolicyDocument.document_type == document_type)
    
    if category:
        query = query.filter(PolicyDocument.category == category)
    
    if department:
        query = query.filter(PolicyDocument.department == department)
    
    if status:
        query = query.filter(PolicyDocument.status == status)
    
    if is_public is not None:
        query = query.filter(PolicyDocument.is_public == is_public)
    
    documents = query.order_by(desc(PolicyDocument.created_at)).offset(skip).limit(limit).all()
    return documents


@router.get("/documents/{document_id}", response_model=PolicyDocumentResponse)
def get_policy_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific policy document"""
    document = db.query(PolicyDocument).filter(PolicyDocument.id == document_id).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy document not found"
        )
    
    if not document.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Document is not public"
        )
    
    # Increment view count
    document.view_count += 1
    
    # Update daily analytics
    today = datetime.now().date()
    analytics = db.query(PolicyAnalytics).filter(
        PolicyAnalytics.policy_document_id == document_id,
        func.date(PolicyAnalytics.analytics_date) == today
    ).first()
    
    if analytics:
        analytics.views += 1
    else:
        analytics = PolicyAnalytics(
            policy_document_id=document_id,
            analytics_date=datetime.now(),
            views=1
        )
        db.add(analytics)
    
    db.commit()
    db.refresh(document)
    return document


@router.put("/documents/{document_id}", response_model=PolicyDocumentResponse)
def update_policy_document(
    document_id: int,
    document_update: PolicyDocumentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a policy document"""
    if current_user.role not in ["admin", "government_official"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    document = db.query(PolicyDocument).filter(PolicyDocument.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy document not found"
        )
    
    # Check permissions
    if current_user.role != "admin" and document.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to edit this document"
        )
    
    for field, value in document_update.dict(exclude_unset=True).items():
        setattr(document, field, value)
    
    db.commit()
    db.refresh(document)
    return document


@router.post("/documents/{document_id}/comments", response_model=PolicyCommentResponse)
def add_policy_comment(
    document_id: int,
    comment: PolicyCommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a comment to a policy document"""
    document = db.query(PolicyDocument).filter(PolicyDocument.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy document not found"
        )
    
    db_comment = PolicyComment(
        **comment.dict(),
        policy_document_id=document_id,
        commenter_id=current_user.id
    )
    
    db.add(db_comment)
    
    # Update analytics
    today = datetime.now().date()
    analytics = db.query(PolicyAnalytics).filter(
        PolicyAnalytics.policy_document_id == document_id,
        func.date(PolicyAnalytics.analytics_date) == today
    ).first()
    
    if analytics:
        analytics.comments_count += 1
    else:
        analytics = PolicyAnalytics(
            policy_document_id=document_id,
            analytics_date=datetime.now(),
            comments_count=1
        )
        db.add(analytics)
    
    db.commit()
    db.refresh(db_comment)
    return db_comment


@router.get("/documents/{document_id}/comments", response_model=List[PolicyCommentResponse])
def get_policy_comments(
    document_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get comments for a policy document"""
    comments = db.query(PolicyComment).filter(
        PolicyComment.policy_document_id == document_id,
        PolicyComment.is_public == True
    ).order_by(desc(PolicyComment.created_at)).offset(skip).limit(limit).all()
    
    return comments


@router.get("/stats", response_model=PolicyStats)
def get_policy_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get policy document statistics"""
    if current_user.role not in ["admin", "government_official"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    total_documents = db.query(PolicyDocument).count()
    active_documents = db.query(PolicyDocument).filter(PolicyDocument.status == "active").count()
    draft_documents = db.query(PolicyDocument).filter(PolicyDocument.status == "draft").count()
    
    # Documents by type
    type_stats = db.query(
        PolicyDocument.document_type, func.count(PolicyDocument.id)
    ).group_by(PolicyDocument.document_type).all()
    documents_by_type = {doc_type: count for doc_type, count in type_stats}
    
    # Documents by category
    category_stats = db.query(
        PolicyDocument.category, func.count(PolicyDocument.id)
    ).group_by(PolicyDocument.category).all()
    documents_by_category = {category: count for category, count in category_stats}
    
    # Documents by department
    dept_stats = db.query(
        PolicyDocument.department, func.count(PolicyDocument.id)
    ).group_by(PolicyDocument.department).all()
    documents_by_department = {dept: count for dept, count in dept_stats}
    
    # Recent documents (last 30 days)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    recent_documents = db.query(PolicyDocument).filter(
        PolicyDocument.created_at >= thirty_days_ago
    ).count()
    
    # Total views and comments
    total_views = db.query(func.sum(PolicyDocument.view_count)).scalar() or 0
    total_comments = db.query(PolicyComment).count()
    
    return PolicyStats(
        total_documents=total_documents,
        active_documents=active_documents,
        draft_documents=draft_documents,
        documents_by_type=documents_by_type,
        documents_by_category=documents_by_category,
        documents_by_department=documents_by_department,
        recent_documents=recent_documents,
        total_views=total_views,
        total_comments=total_comments
    )


@router.get("/documents/{document_id}/analytics", response_model=PolicyAnalyticsReport)
def get_policy_analytics(
    document_id: int,
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed analytics for a policy document"""
    if current_user.role not in ["admin", "government_official"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    document = db.query(PolicyDocument).filter(PolicyDocument.id == document_id).first()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Policy document not found"
        )
    
    # Get analytics data for the period
    analytics_data = db.query(PolicyAnalytics).filter(
        PolicyAnalytics.policy_document_id == document_id,
        PolicyAnalytics.analytics_date >= start_date,
        PolicyAnalytics.analytics_date <= end_date
    ).all()
    
    total_views = sum(record.views for record in analytics_data)
    total_downloads = sum(record.downloads for record in analytics_data)
    total_comments = sum(record.comments_count for record in analytics_data)
    total_citations = sum(record.citations_count for record in analytics_data)
    search_appearances = sum(record.search_appearances for record in analytics_data)
    
    # Calculate engagement score (simplified)
    days_in_period = (end_date - start_date).days or 1
    engagement_score = (total_views + total_comments * 5 + total_citations * 10) / days_in_period
    
    # Extract trending keywords (simplified)
    trending_keywords = []
    if document.keywords:
        trending_keywords = document.keywords.split(',')[:5]
    
    return PolicyAnalyticsReport(
        policy_id=document_id,
        policy_title=document.title,
        period_start=start_date,
        period_end=end_date,
        total_views=total_views,
        total_downloads=total_downloads,
        total_comments=total_comments,
        total_citations=total_citations,
        search_appearances=search_appearances,
        engagement_score=engagement_score,
        trending_keywords=trending_keywords
    )


@router.get("/recommendations", response_model=List[PolicyRecommendation])
def get_policy_recommendations(
    category: Optional[str] = Query(None),
    limit: int = Query(10),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get personalized policy recommendations"""
    # Simplified recommendation algorithm based on user role and popular policies
    query = db.query(PolicyDocument).filter(
        PolicyDocument.status == "active",
        PolicyDocument.is_public == True
    )
    
    if category:
        query = query.filter(PolicyDocument.category == category)
    
    # Get most viewed policies
    popular_policies = query.order_by(desc(PolicyDocument.view_count)).limit(limit).all()
    
    recommendations = []
    for policy in popular_policies:
        reason = f"Popular policy in {policy.category} with {policy.view_count} views"
        confidence = min(1.0, policy.view_count / 100)  # Simplified confidence calculation
        
        recommendations.append(PolicyRecommendation(
            policy_id=policy.id,
            title=policy.title,
            reason=reason,
            confidence_score=confidence,
            category=policy.category
        ))
    
    return recommendations