from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..core.database import Base


class EmissionSource(Base):
    __tablename__ = "emission_sources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    source_type = Column(String(100), nullable=False)  # transport, energy, industrial, agriculture, waste
    location = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    emission_factor = Column(Float, nullable=False)  # CO2 equivalent per unit
    unit = Column(String(50), nullable=False)  # kWh, km, tons, etc.
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    creator = relationship("User")
    emissions = relationship("CarbonEmission", back_populates="emission_source")


class CarbonEmission(Base):
    __tablename__ = "carbon_emissions"
    
    id = Column(Integer, primary_key=True, index=True)
    emission_source_id = Column(Integer, ForeignKey("emission_sources.id"), nullable=False)
    activity_amount = Column(Float, nullable=False)  # Amount of activity (e.g., kWh consumed, km traveled)
    co2_equivalent = Column(Float, nullable=False)  # Calculated CO2 equivalent in tons
    emission_date = Column(DateTime, nullable=False, index=True)
    description = Column(Text, nullable=True)
    verified = Column(Boolean, default=False)
    recorded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    verified_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    emission_source = relationship("EmissionSource", back_populates="emissions")
    recorder = relationship("User", foreign_keys=[recorded_by])
    verifier = relationship("User", foreign_keys=[verified_by])


class CarbonOffset(Base):
    __tablename__ = "carbon_offsets"
    
    id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String(255), nullable=False)
    offset_type = Column(String(100), nullable=False)  # reforestation, renewable_energy, carbon_capture, etc.
    location = Column(String(255), nullable=False)
    co2_offset_tons = Column(Float, nullable=False)
    cost_per_ton = Column(Float, nullable=True)
    total_cost = Column(Float, nullable=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    status = Column(String(50), default="planned")  # planned, active, completed, verified
    description = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    creator = relationship("User")


class CarbonTarget(Base):
    __tablename__ = "carbon_targets"
    
    id = Column(Integer, primary_key=True, index=True)
    target_year = Column(Integer, nullable=False, index=True)
    baseline_year = Column(Integer, nullable=False)
    baseline_emissions = Column(Float, nullable=False)  # Baseline emissions in tons CO2e
    target_emissions = Column(Float, nullable=False)  # Target emissions in tons CO2e
    reduction_percentage = Column(Float, nullable=False)  # Percentage reduction target
    description = Column(Text, nullable=True)
    status = Column(String(50), default="active")  # active, achieved, missed
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    creator = relationship("User")