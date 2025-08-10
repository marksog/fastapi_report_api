from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from .. import schemas, crud, auth, models
from ..database import get_db

router = APIRouter(
    prefix="/potentials",
    tags=["potentials"],
    dependencies=[Depends(auth.get_current_active_user)]
)

@router.post("/", response_model=schemas.Potential, status_code=status.HTTP_201_CREATED)
def create_potential(
    potential: schemas.PotentialCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user)
):
    """
    Create a new potential contact.
    Any authenticated user can create potentials, which will be associated with them as the leader.
    """
    # Set current date if not provided
    if potential.date_added is None:
        potential.date_added = datetime.utcnow()
    
    return crud.create_potential(db=db, potential=potential, leader_id=current_user.id)

@router.get("/", response_model=List[schemas.Potential])
def read_potentials(
    skip: int = 0,
    limit: int = 100,
    is_disciple: Optional[bool] = None,
    location: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user)
):
    """
    Get list of potentials with filters:
    - Admin/Pastor: see all potentials
    - Others: only see potentials they created
    Optional filters:
    - is_disciple: filter by disciple status
    - location: filter by location
    - start_date/end_date: date range filter
    """
    if current_user.role in ["admin", "pastor"]:
        potentials = crud.get_potentials_with_filters(
            db,
            skip=skip,
            limit=limit,
            is_disciple=is_disciple,
            location=location,
            start_date=start_date,
            end_date=end_date
        )
    else:
        potentials = crud.get_potentials_by_leader_with_filters(
            db,
            leader_id=current_user.id,
            skip=skip,
            limit=limit,
            is_disciple=is_disciple,
            location=location,
            start_date=start_date,
            end_date=end_date
        )
    return potentials

@router.get("/{potential_id}", response_model=schemas.Potential)
def read_potential(
    potential_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user)
):
    """
    Get a specific potential by ID.
    Users can only access potentials they created unless they're admin/pastor.
    """
    db_potential = crud.get_potential(db, potential_id=potential_id)
    if db_potential is None:
        raise HTTPException(status_code=404, detail="Potential not found")
    
    # Authorization check
    if current_user.role not in ["admin", "pastor"] and db_potential.leader_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this potential"
        )
    
    return db_potential

@router.put("/{potential_id}", response_model=schemas.Potential)
def update_potential(
    potential_id: int,
    potential: schemas.PotentialCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user)
):
    """
    Update a potential contact.
    Users can only update potentials they created unless they're admin/pastor.
    """
    db_potential = crud.get_potential(db, potential_id=potential_id)
    if db_potential is None:
        raise HTTPException(status_code=404, detail="Potential not found")
    
    # Authorization check
    if current_user.role not in ["admin", "pastor"] and db_potential.leader_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this potential"
        )
    
    # Get changes before update for audit log
    changes = {
        "old": schemas.Potential.from_orm(db_potential).dict(),
        "new": potential.dict()
    }
    
    updated_potential = crud.update_potential(db=db, potential_id=potential_id, potential=potential)
    
    # Log the update
    crud.create_audit_log(
        db=db,
        action="update",
        table_name="potentials",
        record_id=potential_id,
        user_id=current_user.id,
        changes=changes
    )
    
    return updated_potential

@router.delete("/{potential_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_potential(
    potential_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user)
):
    """
    Delete a potential contact.
    Users can only delete potentials they created unless they're admin/pastor.
    """
    db_potential = crud.get_potential(db, potential_id=potential_id)
    if db_potential is None:
        raise HTTPException(status_code=404, detail="Potential not found")
    
    # Authorization check
    if current_user.role not in ["admin", "pastor"] and db_potential.leader_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this potential"
        )
    
    # Log before deletion
    crud.create_audit_log(
        db=db,
        action="delete",
        table_name="potentials",
        record_id=potential_id,
        user_id=current_user.id,
        changes={"deleted_potential": schemas.Potential.from_orm(db_potential).dict()}
    )
    
    crud.delete_potential(db=db, potential_id=potential_id)
    return None

@router.put("/{potential_id}/convert", response_model=schemas.Disciple)
def convert_to_disciple(
    potential_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_active_user)
):
    """
    Convert a potential to a disciple.
    Users can only convert potentials they created unless they're admin/pastor.
    """
    db_potential = crud.get_potential(db, potential_id=potential_id)
    if db_potential is None:
        raise HTTPException(status_code=404, detail="Potential not found")
    
    # Authorization check
    if current_user.role not in ["admin", "pastor"] and db_potential.leader_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to convert this potential"
        )
    
    # Check if already a disciple
    if db_potential.is_disciple:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Potential is already a disciple"
        )
    
    # Convert to disciple
    disciple_data = schemas.DiscipleCreate(
        first_name=db_potential.first_name,
        last_name=db_potential.last_name,
        contact_info=db_potential.contact_info,
        location=db_potential.location,
        notes=db_potential.notes,
        date_added=db_potential.date_added,
        is_worker=False,
        leader_id=db_potential.leader_id
    )
    
    # Create the disciple
    disciple = crud.create_disciple(db=db, disciple=disciple_data, leader_id=current_user.id)
    
    # Update potential to mark as disciple
    crud.update_potential_disciple_status(db=db, potential_id=potential_id, is_disciple=True)
    
    # Log the conversion
    crud.create_audit_log(
        db=db,
        action="convert",
        table_name="potentials",
        record_id=potential_id,
        user_id=current_user.id,
        changes={"converted_to_disciple_id": disciple.id}
    )
    
    return disciple