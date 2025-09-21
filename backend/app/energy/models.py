from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base


class EnergySource(Base):
    __tablename__ = "energy_sources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    source_type = Column(String(100), nullable=False)  # renewable, fossil, nuclear, etc.
    location = Column(String(255), nullable=False)
    capacity_mw = Column(Float, nullable=False)  # Capacity in megawatts
    installation_date = Column(DateTime, nullable=False)
    operational_status = Column(String(50), default="operational")  # operational, maintenance, decommissioned
    description = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    creator = relationship("User")
    consumption_records = relationship("EnergyConsumption", back_populates="energy_source")


class EnergyConsumption(Base):
    __tablename__ = "energy_consumption"
    
    id = Column(Integer, primary_key=True, index=True)
    energy_source_id = Column(Integer, ForeignKey("energy_sources.id"), nullable=False)
    consumption_mwh = Column(Float, nullable=False)  # Consumption in megawatt-hours
    consumption_date = Column(DateTime, nullable=False, index=True)
    cost_per_mwh = Column(Float, nullable=True)
    total_cost = Column(Float, nullable=True)
    meter_reading = Column(Float, nullable=True)
    recorded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    energy_source = relationship("EnergySource", back_populates="consumption_records")
    recorder = relationship("User")


class EnergyProject(Base):
    __tablename__ = "energy_projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    project_type = Column(String(100), nullable=False)  # solar_farm, wind_farm, efficiency_upgrade, etc.
    description = Column(Text, nullable=False)
    location = Column(String(255), nullable=False)
    estimated_capacity_mw = Column(Float, nullable=False)
    estimated_cost = Column(Float, nullable=False)
    actual_cost = Column(Float, nullable=True)
    start_date = Column(DateTime, nullable=False)
    expected_completion = Column(DateTime, nullable=False)
    actual_completion = Column(DateTime, nullable=True)
    status = Column(String(50), default="planned")  # planned, in_progress, completed, cancelled
    project_manager = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    manager = relationship("User")