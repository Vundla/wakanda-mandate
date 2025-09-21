from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class EnergySourceBase(BaseModel):
    name: str
    source_type: str
    location: str
    capacity_mw: float
    installation_date: datetime
    operational_status: str = "operational"
    description: Optional[str] = None


class EnergySourceCreate(EnergySourceBase):
    pass


class EnergySourceUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    capacity_mw: Optional[float] = None
    operational_status: Optional[str] = None
    description: Optional[str] = None


class EnergySourceResponse(EnergySourceBase):
    id: int
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class EnergyConsumptionBase(BaseModel):
    consumption_mwh: float
    consumption_date: datetime
    cost_per_mwh: Optional[float] = None
    total_cost: Optional[float] = None
    meter_reading: Optional[float] = None


class EnergyConsumptionCreate(EnergyConsumptionBase):
    energy_source_id: int


class EnergyConsumptionResponse(EnergyConsumptionBase):
    id: int
    energy_source_id: int
    recorded_by: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class EnergyProjectBase(BaseModel):
    name: str
    project_type: str
    description: str
    location: str
    estimated_capacity_mw: float
    estimated_cost: float
    start_date: datetime
    expected_completion: datetime


class EnergyProjectCreate(EnergyProjectBase):
    pass


class EnergyProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None
    estimated_capacity_mw: Optional[float] = None
    estimated_cost: Optional[float] = None
    actual_cost: Optional[float] = None
    expected_completion: Optional[datetime] = None
    actual_completion: Optional[datetime] = None
    status: Optional[str] = None


class EnergyProjectResponse(EnergyProjectBase):
    id: int
    actual_cost: Optional[float] = None
    actual_completion: Optional[datetime] = None
    status: str
    project_manager: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class EnergyStats(BaseModel):
    total_capacity_mw: float
    total_consumption_last_month: float
    renewable_percentage: float
    operational_sources: int
    total_projects: int
    active_projects: int
    consumption_by_source_type: dict
    monthly_consumption_trend: List[dict]
    cost_savings: float


class EnergyEfficiencyReport(BaseModel):
    period_start: datetime
    period_end: datetime
    total_consumption: float
    average_daily_consumption: float
    peak_consumption_day: datetime
    peak_consumption_amount: float
    efficiency_score: float
    recommendations: List[str]