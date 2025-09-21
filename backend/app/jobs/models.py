from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base


class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    department = Column(String(100), nullable=False, index=True)
    location = Column(String(255), nullable=False)
    job_type = Column(String(50), nullable=False)  # full_time, part_time, contract, internship
    salary_min = Column(Float, nullable=True)
    salary_max = Column(Float, nullable=True)
    requirements = Column(Text, nullable=False)
    responsibilities = Column(Text, nullable=False)
    benefits = Column(Text, nullable=True)
    application_deadline = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    posted_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    poster = relationship("User", back_populates="posted_jobs")
    applications = relationship("JobApplication", back_populates="job")


class JobApplication(Base):
    __tablename__ = "job_applications"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    applicant_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    cover_letter = Column(Text, nullable=True)
    resume_url = Column(String(500), nullable=True)
    status = Column(String(50), default="submitted")  # submitted, reviewed, interview, hired, rejected
    applied_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    job = relationship("Job", back_populates="applications")
    applicant = relationship("User", back_populates="job_applications")