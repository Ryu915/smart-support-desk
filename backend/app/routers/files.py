import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app import models
from app.database import get_db
from app.security import get_current_user


UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB

router = APIRouter()


@router.post("/upload", response_model=int)
async def upload_attachment(
    ticket_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    ticket = db.get(models.Ticket, ticket_id)
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    if current_user.role != "admin" and ticket.creator_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed")

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large",
        )

    ext = Path(file.filename).suffix
    stored_name = f"{uuid.uuid4().hex}{ext}"
    stored_path = UPLOAD_DIR / stored_name
    stored_path.write_bytes(contents)

    attachment = models.Attachment(
        ticket_id=ticket_id,
        filename=file.filename,
        content_type=file.content_type or "application/octet-stream",
        file_path=str(stored_path),
    )
    db.add(attachment)
    db.flush()
    db.add(
        models.TicketEvent(
            ticket_id=ticket.id,
            event_type="ATTACHMENT_ADDED",
            payload=attachment.filename,
        )
    )
    db.commit()
    db.refresh(attachment)

    return attachment.id

from fastapi.responses import FileResponse
from pydantic import BaseModel

class AttachmentRead(BaseModel):
    id: int
    filename: str
    
    class Config:
        from_attributes = True

@router.get("/ticket/{ticket_id}", response_model=list[AttachmentRead])
def get_ticket_attachments(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    attachments = db.query(models.Attachment).filter(models.Attachment.ticket_id == ticket_id).all()
    return attachments

@router.get("/{attachment_id}/download")
def download_attachment(
    attachment_id: int,
    db: Session = Depends(get_db),
):
    attachment = db.get(models.Attachment, attachment_id)
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")
    
    return FileResponse(attachment.file_path, filename=attachment.filename)
