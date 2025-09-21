from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, desc
from typing import List, Optional
from datetime import datetime, timedelta
from ..core.database import get_db
from ..core.auth import get_current_user
from ..users.models import User
from .models import EnergySource, EnergyConsumption, EnergyProject
from .schemas import (
    EnergySourceCreate, EnergySourceResponse, EnergySourceUpdate,
    EnergyConsumptionCreate, EnergyConsumptionResponse,
    EnergyProjectCreate, EnergyProjectResponse, EnergyProjectUpdate,
    EnergyStats, EnergyEfficiencyReport
)

router = APIRouter(prefix="/energy", tags=["energy"])


@router.post("/sources", response_model=EnergySourceResponse)
def create_energy_source(
    source: EnergySourceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new energy source"""
    if current_user.role not in ["admin", "government_official"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    db_source = EnergySource(**source.dict(), created_by=current_user.id)
    db.add(db_source)
    db.commit()
    db.refresh(db_source)
    return db_source


@router.get("/sources", response_model=List[EnergySourceResponse])
def get_energy_sources(
    skip: int = 0,
    limit: int = 100,
    source_type: Optional[str] = Query(None),
    operational_status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get energy sources with filtering"""
    query = db.query(EnergySource)
    
    if source_type:
        query = query.filter(EnergySource.source_type == source_type)
    
    if operational_status:
        query = query.filter(EnergySource.operational_status == operational_status)
    
    sources = query.offset(skip).limit(limit).all()
    return sources


@router.post("/consumption", response_model=EnergyConsumptionResponse)
def record_energy_consumption(
    consumption: EnergyConsumptionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Record energy consumption data"""
    if current_user.role not in ["admin", "government_official"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Verify energy source exists
    source = db.query(EnergySource).filter(EnergySource.id == consumption.energy_source_id).first()
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Energy source not found"
        )
    
    db_consumption = EnergyConsumption(**consumption.dict(), recorded_by=current_user.id)
    db.add(db_consumption)
    db.commit()
    db.refresh(db_consumption)
    return db_consumption


@router.get("/consumption", response_model=List[EnergyConsumptionResponse])
def get_energy_consumption(
    skip: int = 0,
    limit: int = 100,
    energy_source_id: Optional[int] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get energy consumption records"""
    if current_user.role not in ["admin", "government_official"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    query = db.query(EnergyConsumption)
    
    if energy_source_id:
        query = query.filter(EnergyConsumption.energy_source_id == energy_source_id)
    
    if start_date:
        query = query.filter(EnergyConsumption.consumption_date >= start_date)
    
    if end_date:
        query = query.filter(EnergyConsumption.consumption_date <= end_date)
    
    consumption_records = query.order_by(desc(EnergyConsumption.consumption_date)).offset(skip).limit(limit).all()
    return consumption_records


@router.post("/projects", response_model=EnergyProjectResponse)
def create_energy_project(
    project: EnergyProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new energy project"""
    if current_user.role not in ["admin", "government_official"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    db_project = EnergyProject(**project.dict(), project_manager=current_user.id)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


@router.get("/projects", response_model=List[EnergyProjectResponse])
def get_energy_projects(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = Query(None),
    project_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get energy projects with filtering"""
    query = db.query(EnergyProject)
    
    if status:
        query = query.filter(EnergyProject.status == status)
    
    if project_type:
        query = query.filter(EnergyProject.project_type == project_type)
    
    projects = query.offset(skip).limit(limit).all()
    return projects


@router.get("/stats", response_model=EnergyStats)
def get_energy_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive energy statistics and aggregations"""
    if current_user.role not in ["admin", "government_official"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Total capacity
    total_capacity = db.query(func.sum(EnergySource.capacity_mw)).filter(
        EnergySource.operational_status == "operational"
    ).scalar() or 0
    
    # Last month consumption
    last_month = datetime.now() - timedelta(days=30)
    total_consumption_last_month = db.query(func.sum(EnergyConsumption.consumption_mwh)).filter(
        EnergyConsumption.consumption_date >= last_month
    ).scalar() or 0
    
    # Renewable percentage
    renewable_capacity = db.query(func.sum(EnergySource.capacity_mw)).filter(
        EnergySource.operational_status == "operational",
        EnergySource.source_type.in_(["solar", "wind", "hydro", "geothermal", "biomass"])
    ).scalar() or 0
    
    renewable_percentage = (renewable_capacity / total_capacity * 100) if total_capacity > 0 else 0
    
    # Source counts
    operational_sources = db.query(EnergySource).filter(
        EnergySource.operational_status == "operational"
    ).count()
    
    # Project counts
    total_projects = db.query(EnergyProject).count()
    active_projects = db.query(EnergyProject).filter(
        EnergyProject.status.in_(["planned", "in_progress"])
    ).count()
    
    # Consumption by source type
    consumption_by_type = db.query(
        EnergySource.source_type, 
        func.sum(EnergyConsumption.consumption_mwh)
    ).join(EnergyConsumption).filter(
        EnergyConsumption.consumption_date >= last_month
    ).group_by(EnergySource.source_type).all()
    
    consumption_by_source_type = {source_type: float(consumption) for source_type, consumption in consumption_by_type}
    
    # Monthly consumption trend (last 12 months)
    monthly_trend = []
    for i in range(12):
        month_date = datetime.now() - timedelta(days=30*i)
        month_start = month_date.replace(day=1)
        next_month = (month_start + timedelta(days=32)).replace(day=1)
        
        month_consumption = db.query(func.sum(EnergyConsumption.consumption_mwh)).filter(
            EnergyConsumption.consumption_date >= month_start,
            EnergyConsumption.consumption_date < next_month
        ).scalar() or 0
        
        monthly_trend.append({
            'month': month_start.strftime('%Y-%m'),
            'consumption': float(month_consumption)
        })
    
    # Cost savings (simplified calculation)
    renewable_consumption = db.query(func.sum(EnergyConsumption.consumption_mwh)).join(EnergySource).filter(
        EnergySource.source_type.in_(["solar", "wind", "hydro", "geothermal", "biomass"]),
        EnergyConsumption.consumption_date >= last_month
    ).scalar() or 0
    
    # Assuming $50/MWh savings for renewable vs fossil
    cost_savings = renewable_consumption * 50
    
    return EnergyStats(
        total_capacity_mw=total_capacity,
        total_consumption_last_month=total_consumption_last_month,
        renewable_percentage=renewable_percentage,
        operational_sources=operational_sources,
        total_projects=total_projects,
        active_projects=active_projects,
        consumption_by_source_type=consumption_by_source_type,
        monthly_consumption_trend=monthly_trend,
        cost_savings=cost_savings
    )


@router.get("/efficiency-report", response_model=EnergyEfficiencyReport)
def get_efficiency_report(
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate energy efficiency report for a specific period"""
    if current_user.role not in ["admin", "government_official"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Get consumption data for the period
    consumption_data = db.query(EnergyConsumption).filter(
        EnergyConsumption.consumption_date >= start_date,
        EnergyConsumption.consumption_date <= end_date
    ).all()
    
    if not consumption_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No consumption data found for the specified period"
        )
    
    # Calculate metrics
    total_consumption = sum(record.consumption_mwh for record in consumption_data)
    days_in_period = (end_date - start_date).days or 1
    average_daily_consumption = total_consumption / days_in_period
    
    # Find peak consumption day
    daily_consumption = {}
    for record in consumption_data:
        day = record.consumption_date.date()
        if day not in daily_consumption:
            daily_consumption[day] = 0
        daily_consumption[day] += record.consumption_mwh
    
    peak_day = max(daily_consumption.keys(), key=lambda x: daily_consumption[x])
    peak_consumption_amount = daily_consumption[peak_day]
    
    # Calculate efficiency score (simplified)
    # Higher score for lower consumption and higher renewable percentage
    renewable_consumption = sum(
        record.consumption_mwh for record in consumption_data
        if db.query(EnergySource).filter(
            EnergySource.id == record.energy_source_id,
            EnergySource.source_type.in_(["solar", "wind", "hydro", "geothermal", "biomass"])
        ).first()
    )
    
    renewable_ratio = renewable_consumption / total_consumption if total_consumption > 0 else 0
    efficiency_score = min(100, renewable_ratio * 50 + (1 - min(1, average_daily_consumption / 1000)) * 50)
    
    # Generate recommendations
    recommendations = []
    if renewable_ratio < 0.5:
        recommendations.append("Increase renewable energy sources to improve sustainability")
    if average_daily_consumption > 1000:
        recommendations.append("Implement energy conservation measures to reduce consumption")
    if peak_consumption_amount > average_daily_consumption * 2:
        recommendations.append("Consider load balancing to reduce peak consumption")
    
    return EnergyEfficiencyReport(
        period_start=start_date,
        period_end=end_date,
        total_consumption=total_consumption,
        average_daily_consumption=average_daily_consumption,
        peak_consumption_day=datetime.combine(peak_day, datetime.min.time()),
        peak_consumption_amount=peak_consumption_amount,
        efficiency_score=efficiency_score,
        recommendations=recommendations
    )