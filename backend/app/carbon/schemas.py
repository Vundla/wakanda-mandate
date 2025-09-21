from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class EmissionSourceBase(BaseModel):
    name: str
    source_type: str
    location: str
    description: Optional[str] = None
    emission_factor: float
    unit: str


class EmissionSourceCreate(EmissionSourceBase):
    pass


class EmissionSourceUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    emission_factor: Optional[float] = None
    unit: Optional[str] = None
    is_active: Optional[bool] = None


class EmissionSourceResponse(EmissionSourceBase):
    id: int
    is_active: bool
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class CarbonEmissionBase(BaseModel):
    activity_amount: float
    emission_date: datetime
    description: Optional[str] = None


class CarbonEmissionCreate(CarbonEmissionBase):
    emission_source_id: int


class CarbonEmissionResponse(CarbonEmissionBase):
    id: int
    emission_source_id: int
    co2_equivalent: float
    verified: bool
    recorded_by: int
    verified_by: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class CarbonOffsetBase(BaseModel):
    project_name: str
    offset_type: str
    location: str
    co2_offset_tons: float
    cost_per_ton: Optional[float] = None
    total_cost: Optional[float] = None
    start_date: datetime
    end_date: Optional[datetime] = None
    description: Optional[str] = None


class CarbonOffsetCreate(CarbonOffsetBase):
    pass


class CarbonOffsetUpdate(BaseModel):
    project_name: Optional[str] = None
    location: Optional[str] = None
    co2_offset_tons: Optional[float] = None
    cost_per_ton: Optional[float] = None
    total_cost: Optional[float] = None
    end_date: Optional[datetime] = None
    status: Optional[str] = None
    description: Optional[str] = None


class CarbonOffsetResponse(CarbonOffsetBase):
    id: int
    status: str
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class CarbonTargetBase(BaseModel):
    target_year: int
    baseline_year: int
    baseline_emissions: float
    target_emissions: float
    reduction_percentage: float
    description: Optional[str] = None


class CarbonTargetCreate(CarbonTargetBase):
    pass


class CarbonTargetUpdate(BaseModel):
    target_emissions: Optional[float] = None
    reduction_percentage: Optional[float] = None
    description: Optional[str] = None
    status: Optional[str] = None


class CarbonTargetResponse(CarbonTargetBase):
    id: int
    status: str
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class CarbonSummary(BaseModel):
    total_emissions_current_year: float
    total_emissions_last_year: float
    year_over_year_change: float
    emissions_by_source_type: dict
    monthly_emissions_trend: List[dict]
    total_offsets: float
    net_emissions: float
    largest_emission_sources: List[dict]


class EmissionAnalytics(BaseModel):
    period_start: datetime
    period_end: datetime
    total_emissions: float
    verified_emissions: float
    unverified_emissions: float
    emission_intensity: float  # emissions per activity unit
    top_contributors: List[dict]
    reduction_opportunities: List[str]


class CarbonFootprint(BaseModel):
    department: str
    total_emissions: float
    emissions_breakdown: dict
    offset_projects: List[dict]
    net_emissions: float
    reduction_target: Optional[float] = None
    target_progress: Optional[float] = None