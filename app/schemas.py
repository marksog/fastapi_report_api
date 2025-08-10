from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, HttpUrl, Field

class ContactInfo(BaseModel):
    """
    contact information for a person.
    """
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    instagram: Optional[str] = None
    facebook: Optional[str] = None
    twitter: Optional[str] = None
    snapchat: Optional[str] = None
    tiktok: Optional[str] = None

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str
    role: Optional[str] = 'worker'  # Default role is 'worker'
    location: Optional[str] = None

class User(UserBase):
    id: int
    role: str
    is_active: bool = True
    location: Optional[str] = None

    class Config:
        orm_mode = True

class Token(BaseModel):
    username: Optional[str] = None

class PotentialBase(BaseModel):
    first_name: str
    last_name: str
    contact_info: ContactInfo
    location: Optional[str] = None
    notes: Optional[str] = None
    date_added: datetime = Field(default_factory=datetime.utcnow)
    is_disciple: bool = False

class PotentialCreate(PotentialBase):
    pass

class Potential(PotentialBase):
    id: int
    leader_id: int

    class Config:
        orm_mode = True

class DiscipleBase(BaseModel):
    first_name: str
    last_name: str
    contact_info: ContactInfo
    location: Optional[str] = None
    notes: Optional[str] = None
    date_added: datetime = Field(default_factory=datetime.utcnow)
    is_worker: bool = False

class DiscipleCreate(DiscipleBase):
    pass

class Disciple(DiscipleBase):
    id: int
    leader_id: int

    class Config:
        orm_mode = True

class WorkerBase(BaseModel):
    first_name: str
    last_name: str
    contact_info: ContactInfo
    location: Optional[str] = None
    notes: Optional[str] = None
    role: str = 'worker'

class WorkerCreate(WorkerBase):
    pass    

class Worker(WorkerBase):
    id: int
    leader_id: int
    date_added: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        orm_mode = True

class AuditLogBase(BaseModel):
    action: str
    table_name: str
    record_id: int
    changes: Dict[str, Any]

class AuditLog(AuditLogBase):
    id: int
    user_id: int
    timestamp: datetime

    class Config:
        orm_mode = True


