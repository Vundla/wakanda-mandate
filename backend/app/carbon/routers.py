from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, desc
from typing import List, Optional
from datetime import datetime, timedelta
from ..core.database import get_db
from ..core.auth import get_current_user
from ..users.models import User
from .models import EmissionSource, CarbonEmission, CarbonOffset, CarbonTarget
from .schemas import (
    EmissionSourceCreate, EmissionSourceResponse, EmissionSourceUpdate,
    CarbonEmissionCreate, CarbonEmissionResponse,
    CarbonOffsetCreate, CarbonOffsetResponse, CarbonOffsetUpdate,
    CarbonTargetCreate, CarbonTargetResponse, CarbonTargetUpdate,
    CarbonSummary, EmissionAnalytics, CarbonFootprint
)

router = APIRouter(prefix="/carbon", tags=["carbon"])


@router.post("/emission-sources", response_model=EmissionSourceResponse)
def create_emission_source(
    source: EmissionSourceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new emission source"""
    if current_user.role not in ["admin", "government_official"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    db_source = EmissionSource(**source.dict(), created_by=current_user.id)
    db.add(db_source)
    db.commit()
    db.refresh(db_source)
    return db_source


@router.get("/emission-sources", response_model=List[EmissionSourceResponse])
def get_emission_sources(
    skip: int = 0,
    limit: int = 100,
    source_type: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    """Get emission sources with filtering"""
    query = db.query(EmissionSource)
    
    if source_type:
        query = query.filter(EmissionSource.source_type == source_type)
    
    if is_active is not None:
        query = query.filter(EmissionSource.is_active == is_active)
    
    sources = query.offset(skip).limit(limit).all()
    return sources


@router.post("/emissions", response_model=CarbonEmissionResponse)
def record_carbon_emission(
    emission: CarbonEmissionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Record a carbon emission"""
    if current_user.role not in ["admin", "government_official"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Get emission source to calculate CO2 equivalent
    source = db.query(EmissionSource).filter(EmissionSource.id == emission.emission_source_id).first()
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Emission source not found"
        )
    
    # Calculate CO2 equivalent
    co2_equivalent = emission.activity_amount * source.emission_factor
    
    db_emission = CarbonEmission(
        **emission.dict(),
        co2_equivalent=co2_equivalent,
        recorded_by=current_user.id
    )
    
    db.add(db_emission)
    db.commit()
    db.refresh(db_emission)
    return db_emission


@router.put("/emissions/{emission_id}/verify")
def verify_emission(
    emission_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verify a carbon emission record (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can verify emissions"
        )
    
    emission = db.query(CarbonEmission).filter(CarbonEmission.id == emission_id).first()
    if not emission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Emission record not found"
        )
    
    emission.verified = True
    emission.verified_by = current_user.id
    db.commit()
    
    return {"message": "Emission verified successfully"}


@router.post("/offsets", response_model=CarbonOffsetResponse)
def create_carbon_offset(
    offset: CarbonOffsetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a carbon offset project"""
    if current_user.role not in ["admin", "government_official"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    db_offset = CarbonOffset(**offset.dict(), created_by=current_user.id)
    db.add(db_offset)
    db.commit()
    db.refresh(db_offset)
    return db_offset


@router.get("/offsets", response_model=List[CarbonOffsetResponse])
def get_carbon_offsets(
    skip: int = 0,
    limit: int = 100,
    offset_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get carbon offset projects"""
    query = db.query(CarbonOffset)
    
    if offset_type:
        query = query.filter(CarbonOffset.offset_type == offset_type)
    
    if status:
        query = query.filter(CarbonOffset.status == status)
    
    offsets = query.offset(skip).limit(limit).all()
    return offsets


@router.post("/targets", response_model=CarbonTargetResponse)
def create_carbon_target(
    target: CarbonTargetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a carbon reduction target"""
    if current_user.role not in ["admin", "government_official"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    db_target = CarbonTarget(**target.dict(), created_by=current_user.id)
    db.add(db_target)
    db.commit()
    db.refresh(db_target)
    return db_target


@router.get("/summary", response_model=CarbonSummary)
def get_carbon_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive carbon emissions summary"""
    if current_user.role not in ["admin", "government_official"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    current_year = datetime.now().year
    last_year = current_year - 1
    
    # Current year emissions
    current_year_emissions = db.query(func.sum(CarbonEmission.co2_equivalent)).filter(
        extract('year', CarbonEmission.emission_date) == current_year
    ).scalar() or 0
    
    # Last year emissions
    last_year_emissions = db.query(func.sum(CarbonEmission.co2_equivalent)).filter(
        extract('year', CarbonEmission.emission_date) == last_year
    ).scalar() or 0
    
    # Year over year change
    yoy_change = ((current_year_emissions - last_year_emissions) / last_year_emissions * 100) if last_year_emissions > 0 else 0
    
    # Emissions by source type
    emissions_by_type = db.query(
        EmissionSource.source_type,
        func.sum(CarbonEmission.co2_equivalent)
    ).join(CarbonEmission).filter(
        extract('year', CarbonEmission.emission_date) == current_year
    ).group_by(EmissionSource.source_type).all()
    
    emissions_by_source_type = {source_type: float(emissions) for source_type, emissions in emissions_by_type}
    
    # Monthly emissions trend (last 12 months)
    monthly_trend = []
    for i in range(12):
        month_date = datetime.now() - timedelta(days=30*i)
        month_emissions = db.query(func.sum(CarbonEmission.co2_equivalent)).filter(
            extract('month', CarbonEmission.emission_date) == month_date.month,
            extract('year', CarbonEmission.emission_date) == month_date.year
        ).scalar() or 0
        
        monthly_trend.append({
            'month': month_date.strftime('%Y-%m'),
            'emissions': float(month_emissions)
        })
    
    # Total offsets
    total_offsets = db.query(func.sum(CarbonOffset.co2_offset_tons)).filter(
        CarbonOffset.status.in_(["active", "completed", "verified"])
    ).scalar() or 0
    
    # Net emissions
    net_emissions = current_year_emissions - total_offsets
    
    # Largest emission sources
    largest_sources = db.query(
        EmissionSource.name,
        func.sum(CarbonEmission.co2_equivalent).label('total_emissions')
    ).join(CarbonEmission).filter(
        extract('year', CarbonEmission.emission_date) == current_year
    ).group_by(EmissionSource.name).order_by(desc('total_emissions')).limit(5).all()
    
    largest_emission_sources = [
        {'name': name, 'emissions': float(emissions)}
        for name, emissions in largest_sources
    ]
    
    return CarbonSummary(
        total_emissions_current_year=current_year_emissions,
        total_emissions_last_year=last_year_emissions,
        year_over_year_change=yoy_change,
        emissions_by_source_type=emissions_by_source_type,
        monthly_emissions_trend=monthly_trend,
        total_offsets=total_offsets,
        net_emissions=net_emissions,
        largest_emission_sources=largest_emission_sources
    )


@router.get("/analytics", response_model=EmissionAnalytics)
def get_emission_analytics(
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed emission analytics for a specific period"""
    if current_user.role not in ["admin", "government_official"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Get emissions for the period
    emissions = db.query(CarbonEmission).filter(
        CarbonEmission.emission_date >= start_date,
        CarbonEmission.emission_date <= end_date
    ).all()
    
    if not emissions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No emission data found for the specified period"
        )
    
    total_emissions = sum(emission.co2_equivalent for emission in emissions)
    verified_emissions = sum(emission.co2_equivalent for emission in emissions if emission.verified)
    unverified_emissions = total_emissions - verified_emissions
    
    # Calculate emission intensity (emissions per activity unit)
    total_activity = sum(emission.activity_amount for emission in emissions)
    emission_intensity = total_emissions / total_activity if total_activity > 0 else 0
    
    # Top contributors
    source_emissions = {}
    for emission in emissions:
        source_name = db.query(EmissionSource.name).filter(
            EmissionSource.id == emission.emission_source_id
        ).scalar()
        if source_name not in source_emissions:
            source_emissions[source_name] = 0
        source_emissions[source_name] += emission.co2_equivalent
    
    top_contributors = [
        {'source': source, 'emissions': emissions}
        for source, emissions in sorted(source_emissions.items(), key=lambda x: x[1], reverse=True)[:5]
    ]
    
    # Generate reduction opportunities
    reduction_opportunities = []
    if unverified_emissions > total_emissions * 0.2:
        reduction_opportunities.append("Improve emission verification process")
    
    transport_emissions = sum(
        emission.co2_equivalent for emission in emissions
        if db.query(EmissionSource).filter(
            EmissionSource.id == emission.emission_source_id,
            EmissionSource.source_type == "transport"
        ).first()
    )
    
    if transport_emissions > total_emissions * 0.3:
        reduction_opportunities.append("Implement electric vehicle fleet and public transport improvements")
    
    energy_emissions = sum(
        emission.co2_equivalent for emission in emissions
        if db.query(EmissionSource).filter(
            EmissionSource.id == emission.emission_source_id,
            EmissionSource.source_type == "energy"
        ).first()
    )
    
    if energy_emissions > total_emissions * 0.4:
        reduction_opportunities.append("Transition to renewable energy sources")
    
    return EmissionAnalytics(
        period_start=start_date,
        period_end=end_date,
        total_emissions=total_emissions,
        verified_emissions=verified_emissions,
        unverified_emissions=unverified_emissions,
        emission_intensity=emission_intensity,
        top_contributors=top_contributors,
        reduction_opportunities=reduction_opportunities
    )


@router.get("/footprint/{department}", response_model=CarbonFootprint)
def get_department_carbon_footprint(
    department: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get carbon footprint for a specific department"""
    if current_user.role not in ["admin", "government_official"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    current_year = datetime.now().year
    
    # Get department emissions (using emission sources in that location/department)
    department_emissions = db.query(
        func.sum(CarbonEmission.co2_equivalent)
    ).join(EmissionSource).filter(
        EmissionSource.location.ilike(f"%{department}%"),
        extract('year', CarbonEmission.emission_date) == current_year
    ).scalar() or 0
    
    # Emissions breakdown by source type
    breakdown = db.query(
        EmissionSource.source_type,
        func.sum(CarbonEmission.co2_equivalent)
    ).join(CarbonEmission).filter(
        EmissionSource.location.ilike(f"%{department}%"),
        extract('year', CarbonEmission.emission_date) == current_year
    ).group_by(EmissionSource.source_type).all()
    
    emissions_breakdown = {source_type: float(emissions) for source_type, emissions in breakdown}
    
    # Department offset projects
    offset_projects = db.query(CarbonOffset).filter(
        CarbonOffset.location.ilike(f"%{department}%"),
        CarbonOffset.status.in_(["active", "completed", "verified"])
    ).all()
    
    offset_projects_list = [
        {
            'name': project.project_name,
            'type': project.offset_type,
            'offset_tons': project.co2_offset_tons
        }
        for project in offset_projects
    ]
    
    total_offsets = sum(project.co2_offset_tons for project in offset_projects)
    net_emissions = department_emissions - total_offsets
    
    # Check if there's a reduction target for this department
    target = db.query(CarbonTarget).filter(
        CarbonTarget.target_year == current_year,
        CarbonTarget.status == "active"
    ).first()
    
    reduction_target = None
    target_progress = None
    
    if target:
        # Simplified calculation assuming department represents a portion of total target
        reduction_target = target.target_emissions * 0.1  # Assume 10% of total target
        target_progress = (reduction_target - net_emissions) / reduction_target * 100 if reduction_target > 0 else 0
    
    return CarbonFootprint(
        department=department,
        total_emissions=department_emissions,
        emissions_breakdown=emissions_breakdown,
        offset_projects=offset_projects_list,
        net_emissions=net_emissions,
        reduction_target=reduction_target,
        target_progress=target_progress
    )