from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.security import get_current_user


router = APIRouter()


@router.post("/", response_model=schemas.CommentRead, status_code=status.HTTP_201_CREATED)
def add_comment(
    comment_in: schemas.CommentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    ticket = db.get(models.Ticket, comment_in.ticket_id)
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    if current_user.role != "admin" and ticket.creator_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")

    if comment_in.visibility == "INTERNAL" and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can add internal comments",
        )

    comment = models.Comment(
        ticket_id=comment_in.ticket_id,
        author_id=current_user.id,
        body=comment_in.body,
        visibility=comment_in.visibility,
    )

    db.add(comment)
    db.flush()
    db.add(
        models.TicketEvent(
            ticket_id=ticket.id,
            event_type="COMMENT_ADDED",
            payload=f"{comment.visibility.lower()}:{comment.id}",
        )
    )
    db.commit()
    db.refresh(comment)
    return comment


@router.get("/ticket/{ticket_id}", response_model=List[schemas.CommentRead])
def list_comments_for_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    ticket = db.get(models.Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    if current_user.role != "admin" and ticket.creator_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")

    q = db.query(models.Comment).filter(models.Comment.ticket_id == ticket_id)
    if current_user.role != "admin":
        q = q.filter(models.Comment.visibility == "PUBLIC")

    return q.order_by(models.Comment.created_at.asc()).all()

