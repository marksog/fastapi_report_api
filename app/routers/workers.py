from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import schemas, crud, auth
from ..database import get_db

router = APIRouter(
    prefix="/workers",
    tags=["workers"],
    dependencies=[Depends(auth.get_current_active_user)]
)

@router.post("/", response_model=schemas.Worker)
def create_worker(
    worker: schemas.WorkerCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user)
):
    auth.check_admin_or_pastor(current_user)
    return crud.create_worker(db=db, worker=worker, leader_id=current_user.id)

@router.get("/", response_model=List[schemas.Worker])
def read_workers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user)
):
    
    """
    Get list of workers with different access levels:
    - Admin: all workers
    - Pastor: workers in their location
    - Leader: workers they created
    - Worker: not authorized
    """

    if current_user.role == "admin":
        workers = crud.get_workers(db, skip=skip, limit=limit)
    elif current_user.role == "pastor":
        workers = crud.get_workers_by_location(db, location=current_user.location, skip=skip, limit=limit)
    elif current_user.role == "leader":
        workers = crud.get_workers_by_leader(db, leader_id=current_user.id, skip=skip, limit=limit)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view workers"
        )
    return workers

# More endpoints for workers...
@router.get("/{worker_id}", response_model=schemas.Worker)
def read_worker(
    worker_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user)
):
    """
    Get a specific worker by ID with proper authorization checks
    """

    db_worker = crud.get_worker(db, worker_id=worker_id)
    if db_worker is None:
        raise HTTPException(status_code=404, detail="Worker not found")
    
    # Access control
    if current_user.role == "admin":
        return db_worker
    elif current_user.role == "pastor" and db_worker.location == current_user.location:
        return db_worker
    elif current_user.role == "leader" and db_worker.leader_id == current_user.id:
        return db_worker
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this worker"
        )
    
@router.put("/{worker_id}", response_model=schemas.Worker)
def update_worker(
    worker_id: int,
    worker: schemas.WorkerCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user)
):
    """
    Update a specific worker by ID with proper authorization checks
    """

    db_worker = crud.get_worker(db, worker_id=worker_id)
    if db_worker is None:
        raise HTTPException(status_code=404, detail="Worker not found")
    
    # Authorization check
    if current_user.role == "admin":
        pass  # Admin can update any worker
    elif current_user.role == "pastor":
        if db_worker.location != current_user.location:
            raise HTTPException(status_code=403, detail="Not authorized to update this worker")
    elif current_user.role == "leader":
        if db_worker.leader_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to update this worker")
    else:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Get changes before update for audit log
    changes = {
        "old": {k: v for k, v in db_worker.__dict__.items() if not k.startswith('_')},
        "new": worker.dict()
    }
    
    updated_worker = crud.update_worker(db=db, worker_id=worker_id, worker=worker)
    
    # Log the update
    crud.create_audit_log(
        db=db,
        action="update",
        table_name="workers",
        record_id=worker_id,
        user_id=current_user.id,
        changes=changes
    )
    
    return updated_worker

@router.delete("/{worker_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_worker(
    worker_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user)
):
    """
    Delete a worker (only for admin/pastor)
    """
    auth.check_admin_or_pastor(current_user)
    
    db_worker = crud.get_worker(db, worker_id=worker_id)
    if db_worker is None:
        raise HTTPException(status_code=404, detail="Worker not found")
    
    # Additional check for pastor - can only delete in their location
    if current_user.role == "pastor" and db_worker.location != current_user.location:
        raise HTTPException(status_code=403, detail="Can only delete workers in your location")
    
    # Log before deletion
    crud.create_audit_log(
        db=db,
        action="delete",
        table_name="workers",
        record_id=worker_id,
        user_id=current_user.id,
        changes={"deleted_worker": db_worker.__dict__}
    )
    
    crud.delete_worker(db=db, worker_id=worker_id)
    return None

@router.get("/location/{location}", response_model=List[schemas.Worker])
def read_workers_by_location(
    location: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user)
):
    """
    Get workers by location (admin/pastor only)
    """
    auth.check_admin_or_pastor(current_user)
    
    # Additional check for pastor - can only view their own location
    if current_user.role == "pastor" and location != current_user.location:
        raise HTTPException(status_code=403, detail="Can only view workers in your location")
    
    return crud.get_workers_by_location(db, location=location, skip=skip, limit=limit)

@router.get("/role/{role}", response_model=List[schemas.Worker])
def read_workers_by_role(
    role: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user)
):
    """
    Get workers by role (admin only)
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can filter by role")
    
    if role not in ["admin", "pastor", "leader", "worker"]:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    return crud.get_workers_by_role(db, role=role, skip=skip, limit=limit)