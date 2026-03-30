from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.security import get_current_user, require_admin
from app.services.priority_engine import compute_priority
from app.services.sla_engine import calculate_deadline, get_sla_status


router = APIRouter()
VALID_TRANSITIONS = {
    "OPEN": {"IN_PROGRESS"},
    "IN_PROGRESS": {"RESOLVED"},
    "RESOLVED": {"CLOSED", "OPEN"},
    "CLOSED": set(),
}


def record_event(db: Session, ticket: models.Ticket, event_type: str, payload: str = ""):
    event = models.TicketEvent(ticket_id=ticket.id, event_type=event_type, payload=payload)
    db.add(event)


def get_ticket_or_404(db: Session, ticket_id: int) -> models.Ticket:
    ticket = db.get(models.Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    return ticket


def ensure_ticket_access(ticket: models.Ticket, current_user: models.User) -> None:
    if current_user.role != "admin" and ticket.creator_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")


def can_transition(current_status: str, next_status: str) -> bool:
    return next_status in VALID_TRANSITIONS.get(current_status, set())


@router.post("/", response_model=schemas.TicketRead, status_code=status.HTTP_201_CREATED)
def create_ticket(
    ticket_in: schemas.TicketCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    priority = compute_priority(
        impact=ticket_in.impact,
        urgency=ticket_in.urgency,
        category=ticket_in.category,
        reopen_count=0,
    )
    now = datetime.utcnow()
    sla_deadline = calculate_deadline(priority, now)

    ticket = models.Ticket(
        title=ticket_in.title,
        description=ticket_in.description,
        category=ticket_in.category,
        impact=ticket_in.impact,
        urgency=ticket_in.urgency,
        priority=priority,
        creator_id=current_user.id,
        sla_deadline=sla_deadline,
    )
    db.add(ticket)
    db.flush()
    record_event(db, ticket, "TICKET_CREATED")
    record_event(db, ticket, "PRIORITY_COMPUTED", payload=priority)
    db.commit()
    db.refresh(ticket)
    return ticket


@router.get("/", response_model=List[schemas.TicketRead])
def list_tickets(
    search: Optional[str] = Query(default=None),
    status_filter: Optional[str] = Query(default=None),
    category: Optional[str] = Query(default=None),
    priority: Optional[str] = Query(default=None),
    overdue_only: bool = Query(default=False),
    sort_by: str = Query(default="latest", pattern="^(latest|oldest|priority)$"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    q = db.query(models.Ticket)

    if current_user.role != "admin":
        q = q.filter(models.Ticket.creator_id == current_user.id)

    if status_filter:
        q = q.filter(models.Ticket.status == status_filter)
    if category:
        q = q.filter(models.Ticket.category == category)
    if priority:
        q = q.filter(models.Ticket.priority == priority)
    if overdue_only:
        now = datetime.utcnow()
        q = q.filter(models.Ticket.sla_deadline < now)
    if search:
        search_filter = f"%{search}%"
        q = q.filter(
            (models.Ticket.title.ilike(search_filter)) | 
            (models.Ticket.description.ilike(search_filter))
        )

    if sort_by == "latest":
        q = q.order_by(models.Ticket.created_at.desc())
    elif sort_by == "oldest":
        q = q.order_by(models.Ticket.created_at.asc())
    elif sort_by == "priority":
        q = q.order_by(models.Ticket.priority.asc())

    return q.all()


@router.get("/{ticket_id}", response_model=schemas.TicketRead)
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    ticket = get_ticket_or_404(db, ticket_id)
    ensure_ticket_access(ticket, current_user)
    return ticket


@router.patch("/{ticket_id}", response_model=schemas.TicketRead)
def update_ticket_status(
    ticket_id: int,
    ticket_update: schemas.TicketUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    ticket = get_ticket_or_404(db, ticket_id)
    ensure_ticket_access(ticket, current_user)

    if ticket_update.status:
        if not can_transition(ticket.status, ticket_update.status):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status transition",
            )

        old_status = ticket.status
        ticket.status = ticket_update.status
        record_event(
            db,
            ticket,
            "STATUS_CHANGED",
            payload=f"{old_status}->{ticket.status}",
        )

    db.commit()
    db.refresh(ticket)
    return ticket


@router.post("/{ticket_id}/reopen", response_model=schemas.TicketRead)
def reopen_ticket(
    ticket_id: int,
    reopen_request: schemas.TicketReopenRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    ticket = get_ticket_or_404(db, ticket_id)
    ensure_ticket_access(ticket, current_user)

    if ticket.status not in {"RESOLVED", "CLOSED"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only resolved/closed tickets can be reopened",
        )

    ticket.reopen_count += 1
    ticket.status = "OPEN"
    ticket.priority = compute_priority(
        impact=ticket.impact,
        urgency=ticket.urgency,
        category=ticket.category,
        reopen_count=ticket.reopen_count,
    )
    ticket.sla_deadline = calculate_deadline(ticket.priority, datetime.utcnow())

    record_event(db, ticket, "TICKET_REOPENED", payload=reopen_request.reason)
    record_event(db, ticket, "PRIORITY_COMPUTED", payload=ticket.priority)

    db.commit()
    db.refresh(ticket)
    return ticket


@router.get("/{ticket_id}/sla")
def get_ticket_sla(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    ticket = get_ticket_or_404(db, ticket_id)
    ensure_ticket_access(ticket, current_user)

    return get_sla_status(ticket.sla_deadline)


@router.post("/{ticket_id}/override-priority", response_model=schemas.TicketRead)
def override_priority(
    ticket_id: int,
    request: schemas.PriorityOverrideRequest,
    db: Session = Depends(get_db),
    admin: models.User = Depends(require_admin),
):
    _ = admin
    ticket = get_ticket_or_404(db, ticket_id)

    ticket.priority = request.priority
    record_event(db, ticket, "PRIORITY_COMPUTED", payload=f"override:{request.priority}")
    db.commit()
    db.refresh(ticket)
    return ticket


@router.get("/{ticket_id}/events", response_model=List[schemas.TicketEventRead])
def list_ticket_events(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    ticket = get_ticket_or_404(db, ticket_id)
    ensure_ticket_access(ticket, current_user)
    return (
        db.query(models.TicketEvent)
        .filter(models.TicketEvent.ticket_id == ticket_id)
        .order_by(models.TicketEvent.created_at.asc())
        .all()
    )


@router.delete("/{ticket_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    ticket = get_ticket_or_404(db, ticket_id)
    ensure_ticket_access(ticket, current_user)
    db.delete(ticket)
    db.commit()
    return None

