from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_
from typing import List, Optional
from datetime import datetime, timedelta
from ..core.database import get_db
from ..core.auth import get_current_user
from ..users.models import User
from .models import Job, JobApplication
from .schemas import (
    JobCreate, JobResponse, JobUpdate, JobApplicationCreate, 
    JobApplicationResponse, JobSearchFilters, JobStats
)

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/", response_model=JobResponse)
def create_job(
    job: JobCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new job posting (government officials and admins only)"""
    if current_user.role not in ["admin", "government_official"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to create job postings"
        )
    
    db_job = Job(**job.dict(), posted_by=current_user.id)
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job


@router.get("/search", response_model=List[JobResponse])
def search_jobs(
    skip: int = 0,
    limit: int = 100,
    department: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    job_type: Optional[str] = Query(None),
    salary_min: Optional[float] = Query(None),
    salary_max: Optional[float] = Query(None),
    keyword: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Advanced job search with filtering"""
    query = db.query(Job).filter(Job.is_active == True)
    
    # Apply filters
    if department:
        query = query.filter(Job.department.ilike(f"%{department}%"))
    
    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))
    
    if job_type:
        query = query.filter(Job.job_type == job_type)
    
    if salary_min:
        query = query.filter(Job.salary_min >= salary_min)
    
    if salary_max:
        query = query.filter(Job.salary_max <= salary_max)
    
    if keyword:
        query = query.filter(
            or_(
                Job.title.ilike(f"%{keyword}%"),
                Job.description.ilike(f"%{keyword}%"),
                Job.requirements.ilike(f"%{keyword}%")
            )
        )
    
    jobs = query.offset(skip).limit(limit).all()
    return jobs


@router.get("/", response_model=List[JobResponse])
def get_jobs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all active job postings"""
    jobs = db.query(Job).filter(Job.is_active == True).offset(skip).limit(limit).all()
    return jobs


@router.get("/stats", response_model=JobStats)
def get_job_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get job statistics (admin and government officials only)"""
    if current_user.role not in ["admin", "government_official"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    total_jobs = db.query(Job).count()
    active_jobs = db.query(Job).filter(Job.is_active == True).count()
    
    # Jobs by department
    dept_stats = db.query(Job.department, func.count(Job.id)).group_by(Job.department).all()
    jobs_by_department = {dept: count for dept, count in dept_stats}
    
    # Jobs by type
    type_stats = db.query(Job.job_type, func.count(Job.id)).group_by(Job.job_type).all()
    jobs_by_type = {job_type: count for job_type, count in type_stats}
    
    # Total applications
    total_applications = db.query(JobApplication).count()
    
    # Recent posts (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_posts = db.query(Job).filter(Job.created_at >= thirty_days_ago).count()
    
    return JobStats(
        total_jobs=total_jobs,
        active_jobs=active_jobs,
        jobs_by_department=jobs_by_department,
        jobs_by_type=jobs_by_type,
        total_applications=total_applications,
        recent_posts=recent_posts
    )


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):
    """Get job by ID"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    return job


@router.put("/{job_id}", response_model=JobResponse)
def update_job(
    job_id: int,
    job_update: JobUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update job posting"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check permissions
    if current_user.role not in ["admin"] and job.posted_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    for field, value in job_update.dict(exclude_unset=True).items():
        setattr(job, field, value)
    
    db.commit()
    db.refresh(job)
    return job


@router.post("/{job_id}/apply", response_model=JobApplicationResponse)
def apply_for_job(
    job_id: int,
    application: JobApplicationBase,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Apply for a job"""
    # Check if job exists and is active
    job = db.query(Job).filter(Job.id == job_id, Job.is_active == True).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found or inactive"
        )
    
    # Check if user already applied
    existing_application = db.query(JobApplication).filter(
        JobApplication.job_id == job_id,
        JobApplication.applicant_id == current_user.id
    ).first()
    
    if existing_application:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already applied for this job"
        )
    
    # Create application
    db_application = JobApplication(
        job_id=job_id,
        applicant_id=current_user.id,
        cover_letter=application.cover_letter,
        resume_url=application.resume_url
    )
    
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    return db_application


@router.get("/{job_id}/applications", response_model=List[JobApplicationResponse])
def get_job_applications(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get applications for a job (job poster and admins only)"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check permissions
    if current_user.role not in ["admin"] and job.posted_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    applications = db.query(JobApplication).filter(JobApplication.job_id == job_id).all()
    return applications