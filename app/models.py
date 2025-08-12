from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default='worker')  # Default role is 'worker'
    is_active = Column(Boolean, default=True)
    location = Column(String)

    created_potentials = relationship("Potential", back_populates="creator")
    created_disciples = relationship("Disciple", back_populates="creator")
    managed_workers = relationship("Worker", back_populates="manager")

class Potential(Base):
    __tablename__ = 'potentials'

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    contact_info = Column(JSON)  # Store contact info as JSON
    location = Column(String)
    notes = Column(String, nullable=True)
    date_added = Column(DateTime)
    is_disciple = Column(Boolean, default=False)
    creator_id = Column(Integer, ForeignKey('users.id'))

    creator = relationship("User", back_populates="created_potentials")

class Disciple(Base):
    __tablename__ = 'disciples'

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    contact_info = Column(JSON)  # Store contact info as JSON
    location = Column(String)
    notes = Column(String, nullable=True)
    date_added = Column(DateTime)
    creator_id = Column(Integer, ForeignKey('users.id'))

    creator = relationship("User", back_populates="created_disciples")

class Worker(Base):
    __tablename__ = 'workers'

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    contact_info = Column(JSON)  # Store contact info as JSON
    location = Column(String)
    notes = Column(String, nullable=True)
    date_added = Column(DateTime)
    manager_id = Column(Integer, ForeignKey('users.id'))

    manager = relationship("User", back_populates="managed_workers")

class AuditLog(Base):
    __tablename__ = 'audit_logs'

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String)  # e.g., 'create', 'update', 'delete'
    table_name = Column(String)  # e.g., 'potentials', 'disciples', 'workers'
    record_id = Column(Integer)  # ID of the record affected
    changes = Column(JSON)  # Store changes as JSON
    user_id = Column(Integer, ForeignKey('users.id'))
    timestamp = Column(DateTime)
