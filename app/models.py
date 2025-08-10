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

    potentials = relationship("Potential", back_populates="leaders")
    disciples = relationship("Disciple", back_populates="leader")
    workers = relationship("Worker", back_populates="leader")

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
    leader_id = Column(Integer, ForeignKey('users.id'))

    leader = relationship("User", back_populates="potentials")

class Disciple(Base):
    __tablename__ = 'disciples'

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    contact_info = Column(JSON)  # Store contact info as JSON
    location = Column(String)
    notes = Column(String, nullable=True)
    date_added = Column(DateTime)
    leader_id = Column(Integer, ForeignKey('users.id'))

    leader = relationship("User", back_populates="disciples")

class Worker(Base):
    __tablename__ = 'workers'

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    contact_info = Column(JSON)  # Store contact info as JSON
    location = Column(String)
    notes = Column(String, nullable=True)
    date_added = Column(DateTime)
    leader_id = Column(Integer, ForeignKey('users.id'))

    leader = relationship("User", back_populates="workers")

class AuditLog(Base):
    __tablename__ = 'audit_logs'

    id = Column(Integer, primary_key=True, index=True)
    action = Column(String)  # e.g., 'create', 'update', 'delete'
    table_name = Column(String)  # e.g., 'potentials', 'disciples', 'workers'
    record_id = Column(Integer)  # ID of the record affected
    changes = Column(JSON)  # Store changes as JSON
    user_id = Column(Integer, ForeignKey('users.id'))
    timestamp = Column(DateTime)
