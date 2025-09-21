from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class JobBase(BaseModel):
    title: str
    description: str
    department: str
    location: str
    job_type: str
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    requirements: str
    responsibilities: str
    benefits: Optional[str] = None
    application_deadline: Optional[datetime] = None


class JobCreate(JobBase):
    pass


class JobUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    department: Optional[str] = None
    location: Optional[str] = None
    job_type: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    requirements: Optional[str] = None
    responsibilities: Optional[str] = None
    benefits: Optional[str] = None
    application_deadline: Optional[datetime] = None
    is_active: Optional[bool] = None


class JobResponse(JobBase):
    id: int
    is_active: bool
    posted_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class JobApplicationBase(BaseModel):
    cover_letter: Optional[str] = None
    resume_url: Optional[str] = None


class JobApplicationCreate(JobApplicationBase):
    job_id: int


class JobApplicationResponse(JobApplicationBase):
    id: int
    job_id: int
    applicant_id: int
    status: str
    applied_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class JobSearchFilters(BaseModel):
    department: Optional[str] = None
    location: Optional[str] = None
    job_type: Optional[str] = None
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    keyword: Optional[str] = None


class JobStats(BaseModel):
    total_jobs: int
    active_jobs: int
    jobs_by_department: dict
    jobs_by_type: dict
    total_applications: int
    recent_posts: int