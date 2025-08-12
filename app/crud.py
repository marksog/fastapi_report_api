from sqlalchemy.orm import Session
from . import models, schemas, auth
from datetime import datetime
from typing import Optional
import json

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

def create_audit_log(db: Session, action: str, table_name: str, record_id: int, user_id: int, changes: dict):
    # Convert datetime objects to strings in the changes dictionary
    serializable_changes = json.loads(json.dumps(changes, default=json_serial))
    
    db_log = models.AuditLog(
        action=action,
        table_name=table_name,
        record_id=record_id,
        user_id=user_id,
        timestamp=datetime.utcnow(),
        changes=serializable_changes  # Use the serialized version
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

# User operations
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        hashed_password=hashed_password,
        role=user.role,
        location=user.location
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Potential operations
def get_potential(db: Session, potential_id: int):
    return db.query(models.Potential).filter(models.Potential.id == potential_id).first()

def get_potentials(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Potential).offset(skip).limit(limit).all()

def get_potentials_by_creator(db: Session, creator_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Potential).filter(models.Potential.creator_id == creator_id).offset(skip).limit(limit).all()

from datetime import datetime

def create_potential(db: Session, potential: schemas.PotentialCreate, creator_id: int):
    # Convert to dict and handle date_added
    potential_dict = potential.dict()
    
    # Set current datetime if date_added is not provided
    if not potential_dict.get('date_added'):
        potential_dict['date_added'] = datetime.utcnow()
    
    # Ensure date_added is serializable (convert datetime to ISO format string)
    if isinstance(potential_dict['date_added'], datetime):
        potential_dict['date_added'] = potential_dict['date_added'].isoformat()
    
    # Create the potential
    db_potential = models.Potential(**potential_dict, creator_id=creator_id)
    db.add(db_potential)
    db.commit()
    db.refresh(db_potential)
    
    # Create audit log with serialized data
    create_audit_log(
        db=db,
        action="create",
        table_name="potentials",
        record_id=db_potential.id,
        user_id=creator_id,
        changes=potential_dict
    )
    
    return db_potential

def update_potential(db: Session, potential_id: int, potential: schemas.PotentialCreate, user_id: int):
    db_potential = db.query(models.Potential).filter(models.Potential.id == potential_id).first()
    if not db_potential:
        return None

    changes = {}
    potential_dict = potential.dict()
    
    for key, value in potential_dict.items():
        # Skip date_added in updates to prevent modification
        if key == 'date_added':
            continue
            
        if getattr(db_potential, key) != value:
            # Serialize datetime objects if they exist in other fields
            if isinstance(value, datetime):
                value = value.isoformat()
            old_value = getattr(db_potential, key)
            if isinstance(old_value, datetime):
                old_value = old_value.isoformat()
            changes[key] = (old_value, value)
            setattr(db_potential, key, value)

    db.commit()
    db.refresh(db_potential)

    create_audit_log(
        db=db,
        action='update',
        table_name='potentials',
        record_id=db_potential.id,
        user_id=user_id,
        changes=changes
    )
    return db_potential

def delete_potential(db: Session, potential_id: int, user_id: int):
    db_potential = db.query(models.Potential).filter(models.Potential.id == potential_id).first()
    if not db_potential:
        return None

    db.delete(db_potential)
    db.commit()

    # log the deletion
    create_audit_log(
        db=db,
        action='delete',
        table_name='potentials',
        record_id=potential_id,
        user_id=user_id,
        changes={'deleted': True}
    )
    return db_potential

# Disciple Operations
def get_disciple(db: Session, disciple_id: int):
    return db.query(models.Disciple).filter(models.Disciple.id == disciple_id).first()

def get_disciples(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Disciple).offset(skip).limit(limit).all()

def get_disciples_by_creator(db: Session, creator_id: int, skip: int = 0, limit: int = 10):
    return db.query(models.Disciple).filter(models.Disciple.creator_id == creator_id).offset(skip).limit(limit).all()

def create_disciple(db: Session, disciple: schemas.DiscipleCreate, creator_id: int):
    db_disciple = models.Disciple(**disciple.dict(), creator_id=creator_id, date_added=datetime.utcnow())
    db.add(db_disciple)
    db.commit()
    db.refresh(db_disciple)

    # log the creation
    create_audit_log(
        db=db,
        action='create',
        table_name='disciples',
        record_id=db_disciple.id,
        user_id=creator_id,
        changes=disciple.dict()
    )
    return db_disciple

def update_disciple(db: Session, disciple_id: int, disciple: schemas.DiscipleCreate, user_id: int): 
    db_disciple = db.query(models.Disciple).filter(models.Disciple.id == disciple_id).first()
    if not db_disciple:
        return None

    changes = {}
    for key, value in disciple.dict().items():
        if getattr(db_disciple, key) != value:
            changes[key] = (getattr(db_disciple, key), value)
            setattr(db_disciple, key, value)

    db.commit()
    db.refresh(db_disciple)

    # log the update
    create_audit_log(
        db=db,
        action='update',
        table_name='disciples',
        record_id=db_disciple.id,
        user_id=user_id,
        changes=changes
    )
    return db_disciple

def delete_disciple(db: Session, disciple_id: int, user_id: int):
    db_disciple = db.query(models.Disciple).filter(models.Disciple.id == disciple_id).first()
    if not db_disciple:
        return None

    db.delete(db_disciple)
    db.commit()

    # log the deletion
    create_audit_log(
        db=db,
        action='delete',
        table_name='disciples',
        record_id=disciple_id,
        user_id=user_id,
        changes={'deleted': True}
    )
    return db_disciple

# Worker Operations
def get_worker(db: Session, worker_id: int):
    return db.query(models.Worker).filter(models.Worker.id == worker_id).first()

def get_workers(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Worker).offset(skip).limit(limit).all()

def get_workers_by_manager(db: Session, manager_id: int, skip: int = 0, limit: int = 10):
    return db.query(models.Worker).filter(models.Worker.manager_id == manager_id).offset(skip).limit(limit).all()

def create_worker(db: Session, worker: schemas.WorkerCreate, manager_id: int):
    db_worker = models.Worker(**worker.dict(), manager_id=manager_id, date_added=datetime.utcnow())
    db.add(db_worker)
    db.commit()
    db.refresh(db_worker)

    # log the creation
    create_audit_log(
        db=db,
        action='create',
        table_name='workers',
        record_id=db_worker.id,
        user_id=manager_id,
        changes=worker.dict()
    )
    return db_worker

def update_worker(db: Session, worker_id: int, worker: schemas.WorkerCreate, user_id: int):
    db_worker = db.query(models.Worker).filter(models.Worker.id == worker_id).first()
    if not db_worker:
        return None

    changes = {}
    for key, value in worker.dict().items():
        if getattr(db_worker, key) != value:
            changes[key] = (getattr(db_worker, key), value)
            setattr(db_worker, key, value)

    db.commit()
    db.refresh(db_worker)

    # log the update
    create_audit_log(
        db=db,
        action='update',
        table_name='workers',
        record_id=db_worker.id,
        user_id=user_id,
        changes=changes
    )
    return db_worker

def delete_worker(db: Session, worker_id: int, user_id: int):
    db_worker = db.query(models.Worker).filter(models.Worker.id == worker_id).first()
    if not db_worker:
        return None

    db.delete(db_worker)
    db.commit()

    # log the deletion
    create_audit_log(
        db=db,
        action='delete',
        table_name='workers',
        record_id=worker_id,
        user_id=user_id,
        changes={'deleted': True}
    )
    return db_worker

def get_potentials_with_filters(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    is_disciple: Optional[bool] = None,
    location: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    query = db.query(models.Potential)
    
    if is_disciple is not None:
        query = query.filter(models.Potential.is_disciple == is_disciple)
    if location:
        query = query.filter(models.Potential.location == location)
    if start_date:
        query = query.filter(models.Potential.date_added >= start_date)
    if end_date:
        query = query.filter(models.Potential.date_added <= end_date)
    
    return query.offset(skip).limit(limit).all()

def get_potentials_by_creator_with_filters(
    db: Session,
    creator_id: int,
    skip: int = 0,
    limit: int = 100,
    is_disciple: Optional[bool] = None,
    location: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    query = db.query(models.Potential).filter(models.Potential.creator_id == creator_id)
    
    if is_disciple is not None:
        query = query.filter(models.Potential.is_disciple == is_disciple)
    if location:
        query = query.filter(models.Potential.location == location)
    if start_date:
        query = query.filter(models.Potential.date_added >= start_date)
    if end_date:
        query = query.filter(models.Potential.date_added <= end_date)
    
    return query.offset(skip).limit(limit).all()

def update_potential_disciple_status(db: Session, potential_id: int, is_disciple: bool):
    db_potential = db.query(models.Potential).filter(models.Potential.id == potential_id).first()
    if db_potential:
        db_potential.is_disciple = is_disciple
        db.commit()
        db.refresh(db_potential)
    return db_potential