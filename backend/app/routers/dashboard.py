from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.security import require_admin


router = APIRouter()


def seconds_to_hours(seconds: float | None) -> float | None:
    if seconds is None:
        return None
    return round(seconds / 3600.0, 2)


@router.get("/", response_model=schemas.DashboardStats)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    admin_user=Depends(require_admin),
):
    total_tickets = db.query(models.Ticket).count()
    open_tickets = db.query(models.Ticket).filter(models.Ticket.status == "OPEN").count()

    now = datetime.utcnow()
    overdue_tickets = (
        db.query(models.Ticket)
        .filter(models.Ticket.sla_deadline < now)
        .count()
    )

    seven_days_ago = now - timedelta(days=7)
    closed_tickets = (
        db.query(models.Ticket.created_at, models.Ticket.updated_at)
        .filter(models.Ticket.status == "CLOSED")
        .filter(models.Ticket.updated_at >= seven_days_ago)
        .all()
    )
    
    if closed_tickets:
        total_seconds = sum((row.updated_at - row.created_at).total_seconds() for row in closed_tickets)
        avg_seconds = total_seconds / len(closed_tickets)
    else:
        avg_seconds = None

    avg_resolution_time_hours = seconds_to_hours(avg_seconds)

    category_counts_rows = (
        db.query(models.Ticket.category, func.count(models.Ticket.id))
        .group_by(models.Ticket.category)
        .all()
    )
    category_counts = {row[0]: row[1] for row in category_counts_rows}

    return schemas.DashboardStats(
        total_tickets=total_tickets,
        open_tickets=open_tickets,
        overdue_tickets=overdue_tickets,
        avg_resolution_time_hours=avg_resolution_time_hours,
        category_counts=category_counts,
    )

