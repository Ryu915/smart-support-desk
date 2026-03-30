from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, constr


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: constr(min_length=6)


class UserRead(UserBase):
    id: int
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TicketBase(BaseModel):
    title: constr(min_length=5)
    description: constr(min_length=10)
    category: str
    impact: str
    urgency: str


class TicketCreate(TicketBase):
    attachment_id: Optional[int] = None


class TicketUpdate(BaseModel):
    status: Optional[str] = None


class TicketReopenRequest(BaseModel):
    reason: constr(min_length=5)


class PriorityOverrideRequest(BaseModel):
    priority: str


class TicketRead(TicketBase):
    id: int
    priority: str
    status: str
    reopen_count: int
    sla_deadline: datetime
    created_at: datetime
    updated_at: datetime
    creator_id: int

    class Config:
        from_attributes = True


class CommentBase(BaseModel):
    body: constr(min_length=1)


class CommentCreate(CommentBase):
    ticket_id: int
    visibility: str = "PUBLIC"


class CommentRead(CommentBase):
    id: int
    ticket_id: int
    author_id: int
    visibility: str
    created_at: datetime

    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    total_tickets: int
    open_tickets: int
    overdue_tickets: int
    avg_resolution_time_hours: Optional[float]
    category_counts: dict


class TicketEventRead(BaseModel):
    id: int
    ticket_id: int
    event_type: str
    payload: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

