from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base


class PolicyDocument(Base):
    __tablename__ = "policy_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    document_number = Column(String(100), unique=True, nullable=False, index=True)
    document_type = Column(String(100), nullable=False)  # law, regulation, policy, guideline, etc.
    category = Column(String(100), nullable=False, index=True)  # healthcare, education, environment, etc.
    department = Column(String(100), nullable=False)
    summary = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    keywords = Column(Text, nullable=True)  # Comma-separated keywords
    effective_date = Column(DateTime, nullable=False)
    expiry_date = Column(DateTime, nullable=True)
    status = Column(String(50), default="active")  # draft, active, superseded, repealed
    version = Column(String(20), default="1.0")
    language = Column(String(10), default="en")
    file_url = Column(String(500), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_public = Column(Boolean, default=True)
    view_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    reviewer = relationship("User", foreign_keys=[reviewed_by])
    amendments = relationship("PolicyAmendment", back_populates="policy_document")
    comments = relationship("PolicyComment", back_populates="policy_document")
    citations = relationship("PolicyCitation", back_populates="citing_document")


class PolicyAmendment(Base):
    __tablename__ = "policy_amendments"
    
    id = Column(Integer, primary_key=True, index=True)
    policy_document_id = Column(Integer, ForeignKey("policy_documents.id"), nullable=False)
    amendment_number = Column(String(50), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    changes_summary = Column(Text, nullable=False)
    effective_date = Column(DateTime, nullable=False)
    status = Column(String(50), default="proposed")  # proposed, approved, rejected, implemented
    proposed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    policy_document = relationship("PolicyDocument", back_populates="amendments")
    proposer = relationship("User", foreign_keys=[proposed_by])
    approver = relationship("User", foreign_keys=[approved_by])


class PolicyComment(Base):
    __tablename__ = "policy_comments"
    
    id = Column(Integer, primary_key=True, index=True)
    policy_document_id = Column(Integer, ForeignKey("policy_documents.id"), nullable=False)
    comment_text = Column(Text, nullable=False)
    comment_type = Column(String(50), default="feedback")  # feedback, question, suggestion, objection
    is_public = Column(Boolean, default=True)
    commenter_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    response = Column(Text, nullable=True)
    responded_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    policy_document = relationship("PolicyDocument", back_populates="comments")
    commenter = relationship("User", foreign_keys=[commenter_id])
    responder = relationship("User", foreign_keys=[responded_by])


class PolicyCitation(Base):
    __tablename__ = "policy_citations"
    
    id = Column(Integer, primary_key=True, index=True)
    citing_document_id = Column(Integer, ForeignKey("policy_documents.id"), nullable=False)
    cited_document_id = Column(Integer, ForeignKey("policy_documents.id"), nullable=False)
    citation_context = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    citing_document = relationship("PolicyDocument", foreign_keys=[citing_document_id], back_populates="citations")
    cited_document = relationship("PolicyDocument", foreign_keys=[cited_document_id])


class PolicyAnalytics(Base):
    __tablename__ = "policy_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    policy_document_id = Column(Integer, ForeignKey("policy_documents.id"), nullable=False)
    analytics_date = Column(DateTime, nullable=False, index=True)
    views = Column(Integer, default=0)
    downloads = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    citations_count = Column(Integer, default=0)
    search_appearances = Column(Integer, default=0)
    
    # Relationships
    policy_document = relationship("PolicyDocument")