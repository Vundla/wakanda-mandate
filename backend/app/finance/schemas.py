from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class BudgetBase(BaseModel):
    department: str
    fiscal_year: int
    category: str
    allocated_amount: float
    description: Optional[str] = None


class BudgetCreate(BudgetBase):
    pass


class BudgetUpdate(BaseModel):
    department: Optional[str] = None
    category: Optional[str] = None
    allocated_amount: Optional[float] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class BudgetResponse(BudgetBase):
    id: int
    spent_amount: float
    created_by: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class TransactionBase(BaseModel):
    amount: float
    transaction_type: str
    description: str
    vendor: Optional[str] = None
    invoice_number: Optional[str] = None
    transaction_date: datetime


class TransactionCreate(TransactionBase):
    budget_id: int


class TransactionUpdate(BaseModel):
    amount: Optional[float] = None
    description: Optional[str] = None
    vendor: Optional[str] = None
    invoice_number: Optional[str] = None
    transaction_date: Optional[datetime] = None
    status: Optional[str] = None


class TransactionResponse(TransactionBase):
    id: int
    budget_id: int
    approved_by: Optional[int] = None
    status: str
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class RevenueBase(BaseModel):
    source: str
    amount: float
    revenue_date: datetime
    description: Optional[str] = None
    fiscal_year: int


class RevenueCreate(RevenueBase):
    pass


class RevenueResponse(RevenueBase):
    id: int
    created_by: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class FinanceAnalytics(BaseModel):
    total_budget: float
    total_spent: float
    total_revenue: float
    budget_utilization: float
    department_spending: dict
    category_spending: dict
    monthly_trends: List[dict]
    pending_transactions: int


class BudgetSummary(BaseModel):
    department: str
    fiscal_year: int
    total_allocated: float
    total_spent: float
    utilization_rate: float
    remaining_budget: float