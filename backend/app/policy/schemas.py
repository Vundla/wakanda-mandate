from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime


class PolicyDocumentBase(BaseModel):
    title: str
    document_number: str
    document_type: str
    category: str
    department: str
    summary: str
    content: str
    keywords: Optional[str] = None
    effective_date: datetime
    expiry_date: Optional[datetime] = None
    version: str = "1.0"
    language: str = "en"
    file_url: Optional[str] = None
    is_public: bool = True


class PolicyDocumentCreate(PolicyDocumentBase):
    pass


class PolicyDocumentUpdate(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    keywords: Optional[str] = None
    expiry_date: Optional[datetime] = None
    status: Optional[str] = None
    file_url: Optional[str] = None
    is_public: Optional[bool] = None


class PolicyDocumentResponse(PolicyDocumentBase):
    id: int
    status: str
    created_by: int
    reviewed_by: Optional[int] = None
    view_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class PolicyAmendmentBase(BaseModel):
    amendment_number: str
    title: str
    description: str
    changes_summary: str
    effective_date: datetime


class PolicyAmendmentCreate(PolicyAmendmentBase):
    policy_document_id: int


class PolicyAmendmentResponse(PolicyAmendmentBase):
    id: int
    policy_document_id: int
    status: str
    proposed_by: int
    approved_by: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class PolicyCommentBase(BaseModel):
    comment_text: str
    comment_type: str = "feedback"
    is_public: bool = True


class PolicyCommentCreate(PolicyCommentBase):
    policy_document_id: int


class PolicyCommentResponse(PolicyCommentBase):
    id: int
    policy_document_id: int
    commenter_id: int
    response: Optional[str] = None
    responded_by: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class PolicySearchFilters(BaseModel):
    document_type: Optional[str] = None
    category: Optional[str] = None
    department: Optional[str] = None
    status: Optional[str] = None
    effective_date_from: Optional[datetime] = None
    effective_date_to: Optional[datetime] = None
    language: Optional[str] = None
    keyword: Optional[str] = None


class PolicySearchResult(BaseModel):
    id: int
    title: str
    document_number: str
    document_type: str
    category: str
    department: str
    summary: str
    effective_date: datetime
    status: str
    relevance_score: Optional[float] = None
    
    class Config:
        from_attributes = True


class PolicyStats(BaseModel):
    total_documents: int
    active_documents: int
    draft_documents: int
    documents_by_type: Dict[str, int]
    documents_by_category: Dict[str, int]
    documents_by_department: Dict[str, int]
    recent_documents: int
    total_views: int
    total_comments: int


class PolicyAnalyticsReport(BaseModel):
    policy_id: int
    policy_title: str
    period_start: datetime
    period_end: datetime
    total_views: int
    total_downloads: int
    total_comments: int
    total_citations: int
    search_appearances: int
    engagement_score: float
    trending_keywords: List[str]


class PolicyRecommendation(BaseModel):
    policy_id: int
    title: str
    reason: str
    confidence_score: float
    category: str


class PolicyImpactAnalysis(BaseModel):
    policy_id: int
    affected_departments: List[str]
    estimated_impact: str
    implementation_cost: Optional[float] = None
    compliance_requirements: List[str]
    related_policies: List[int]
    risk_assessment: str
    recommendations: List[str]


class CitationNetwork(BaseModel):
    policy_id: int
    title: str
    inbound_citations: List[Dict[str, str]]
    outbound_citations: List[Dict[str, str]]
    citation_score: float
    influence_rank: int