from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from typing import List, Optional
from datetime import datetime, timedelta
from ..core.database import get_db
from ..core.auth import get_current_user
from ..users.models import User
from .models import Budget, Transaction, Revenue
from .schemas import (
    BudgetCreate, BudgetResponse, BudgetUpdate, TransactionCreate,
    TransactionResponse, TransactionUpdate, RevenueCreate, RevenueResponse,
    FinanceAnalytics, BudgetSummary
)

router = APIRouter(prefix="/finance", tags=["finance"])


@router.post("/budgets", response_model=BudgetResponse)
def create_budget(
    budget: BudgetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new budget (admin and government officials only)"""
    if current_user.role not in ["admin", "government_official"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    db_budget = Budget(**budget.dict(), created_by=current_user.id)
    db.add(db_budget)
    db.commit()
    db.refresh(db_budget)
    return db_budget


@router.get("/budgets", response_model=List[BudgetResponse])
def get_budgets(
    skip: int = 0,
    limit: int = 100,
    department: Optional[str] = Query(None),
    fiscal_year: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get budgets with filtering"""
    if current_user.role not in ["admin", "government_official"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    query = db.query(Budget).filter(Budget.is_active == True)
    
    if department:
        query = query.filter(Budget.department.ilike(f"%{department}%"))
    
    if fiscal_year:
        query = query.filter(Budget.fiscal_year == fiscal_year)
    
    budgets = query.offset(skip).limit(limit).all()
    return budgets


@router.get("/budgets/summary", response_model=List[BudgetSummary])
def get_budget_summary(
    fiscal_year: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get budget summary by department"""
    if current_user.role not in ["admin", "government_official"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    query = db.query(Budget).filter(Budget.is_active == True)
    if fiscal_year:
        query = query.filter(Budget.fiscal_year == fiscal_year)
    
    budgets = query.all()
    
    # Group by department and fiscal year
    summary_dict = {}
    for budget in budgets:
        key = (budget.department, budget.fiscal_year)
        if key not in summary_dict:
            summary_dict[key] = {
                'department': budget.department,
                'fiscal_year': budget.fiscal_year,
                'total_allocated': 0,
                'total_spent': 0
            }
        
        summary_dict[key]['total_allocated'] += budget.allocated_amount
        summary_dict[key]['total_spent'] += budget.spent_amount
    
    # Convert to response format
    summaries = []
    for summary in summary_dict.values():
        utilization_rate = (summary['total_spent'] / summary['total_allocated'] * 100) if summary['total_allocated'] > 0 else 0
        remaining_budget = summary['total_allocated'] - summary['total_spent']
        
        summaries.append(BudgetSummary(
            department=summary['department'],
            fiscal_year=summary['fiscal_year'],
            total_allocated=summary['total_allocated'],
            total_spent=summary['total_spent'],
            utilization_rate=utilization_rate,
            remaining_budget=remaining_budget
        ))
    
    return summaries


@router.post("/transactions", response_model=TransactionResponse)
def create_transaction(
    transaction: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new transaction"""
    if current_user.role not in ["admin", "government_official"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Check if budget exists
    budget = db.query(Budget).filter(Budget.id == transaction.budget_id).first()
    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found"
        )
    
    db_transaction = Transaction(**transaction.dict(), created_by=current_user.id)
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


@router.put("/transactions/{transaction_id}/approve")
def approve_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Approve a transaction (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    transaction.status = "approved"
    transaction.approved_by = current_user.id
    
    # Update budget spent amount if it's an expense
    if transaction.transaction_type == "expense":
        budget = db.query(Budget).filter(Budget.id == transaction.budget_id).first()
        if budget:
            budget.spent_amount += transaction.amount
    
    db.commit()
    return {"message": "Transaction approved successfully"}


@router.post("/revenues", response_model=RevenueResponse)
def create_revenue(
    revenue: RevenueCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Record new revenue"""
    if current_user.role not in ["admin", "government_official"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    db_revenue = Revenue(**revenue.dict(), created_by=current_user.id)
    db.add(db_revenue)
    db.commit()
    db.refresh(db_revenue)
    return db_revenue


@router.get("/analytics", response_model=FinanceAnalytics)
def get_finance_analytics(
    fiscal_year: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive finance analytics"""
    if current_user.role not in ["admin", "government_official"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Filter by fiscal year if provided
    budget_query = db.query(Budget)
    revenue_query = db.query(Revenue)
    transaction_query = db.query(Transaction)
    
    if fiscal_year:
        budget_query = budget_query.filter(Budget.fiscal_year == fiscal_year)
        revenue_query = revenue_query.filter(Revenue.fiscal_year == fiscal_year)
        transaction_query = transaction_query.join(Budget).filter(Budget.fiscal_year == fiscal_year)
    
    # Calculate totals
    total_budget = budget_query.with_entities(func.sum(Budget.allocated_amount)).scalar() or 0
    total_spent = budget_query.with_entities(func.sum(Budget.spent_amount)).scalar() or 0
    total_revenue = revenue_query.with_entities(func.sum(Revenue.amount)).scalar() or 0
    
    budget_utilization = (total_spent / total_budget * 100) if total_budget > 0 else 0
    
    # Department spending
    dept_spending = budget_query.with_entities(
        Budget.department, func.sum(Budget.spent_amount)
    ).group_by(Budget.department).all()
    department_spending = {dept: float(amount) for dept, amount in dept_spending}
    
    # Category spending
    cat_spending = budget_query.with_entities(
        Budget.category, func.sum(Budget.spent_amount)
    ).group_by(Budget.category).all()
    category_spending = {cat: float(amount) for cat, amount in cat_spending}
    
    # Monthly trends (last 12 months)
    monthly_trends = []
    for i in range(12):
        month_date = datetime.now() - timedelta(days=30*i)
        month_transactions = transaction_query.filter(
            extract('month', Transaction.transaction_date) == month_date.month,
            extract('year', Transaction.transaction_date) == month_date.year,
            Transaction.status == 'approved'
        ).with_entities(func.sum(Transaction.amount)).scalar() or 0
        
        monthly_trends.append({
            'month': month_date.strftime('%Y-%m'),
            'amount': float(month_transactions)
        })
    
    # Pending transactions
    pending_transactions = transaction_query.filter(Transaction.status == 'pending').count()
    
    return FinanceAnalytics(
        total_budget=total_budget,
        total_spent=total_spent,
        total_revenue=total_revenue,
        budget_utilization=budget_utilization,
        department_spending=department_spending,
        category_spending=category_spending,
        monthly_trends=monthly_trends,
        pending_transactions=pending_transactions
    )