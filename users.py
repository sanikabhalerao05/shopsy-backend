from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from typing import List
import os, uuid, shutil
import database, models, schemas, auth_utils

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=List[schemas.UserOut])
def get_users(db: Session = Depends(database.get_db), current_user: models.User = Depends(auth_utils.get_admin_user)):
    return db.query(models.User).filter(models.User.role == "user").all()

@router.get("/profile", response_model=schemas.UserOut)
def get_profile(current_user: models.User = Depends(auth_utils.get_current_user)):
    return current_user

@router.put("/profile", response_model=schemas.UserOut)
def update_profile(user_update: schemas.UserUpdate, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth_utils.get_current_user)):
    update_data = user_update.model_dump(exclude_unset=True)
    if "name" in update_data:
        current_user.name = update_data["name"]
    if "address" in update_data:
        current_user.address = update_data["address"]
    if "contact" in update_data:
        current_user.contact = update_data["contact"]
    if "profile_photo" in update_data:
        current_user.profile_photo = update_data["profile_photo"]
    
    # Admin can update status of any user (this is a bit simplified, but follows the admin role)
    # Actually, let's add a separate endpoint for admin to update status if needed, 
    # but for profile update, only basic info.
    
    db.commit()
    db.refresh(current_user)
    return current_user

@router.post("/profile-photo", response_model=schemas.UserOut)
async def upload_profile_photo(
    file: UploadFile = File(...), 
    db: Session = Depends(database.get_db), 
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Create directory if not exists
    upload_dir = "uploads/profile_photos"
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    
    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(upload_dir, filename)
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Delete old photo if exists
    if current_user.profile_photo and current_user.profile_photo.startswith("uploads/"):
        if os.path.exists(current_user.profile_photo):
            os.remove(current_user.profile_photo)
            
    # Update DB - store relative path for easier serving
    current_user.profile_photo = file_path.replace("\\", "/") # Ensure web-friendly slashes
    db.commit()
    db.refresh(current_user)
    return current_user

@router.delete("/profile-photo", response_model=schemas.UserOut)
def delete_profile_photo(
    db: Session = Depends(database.get_db), 
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    # Delete file if exists
    if current_user.profile_photo and current_user.profile_photo.startswith("uploads/"):
        if os.path.exists(current_user.profile_photo):
            os.remove(current_user.profile_photo)
            
    current_user.profile_photo = None
    db.commit()
    db.refresh(current_user)
    return current_user

@router.put("/{user_id}/status", response_model=schemas.UserOut)
def update_user_status(user_id: int, status_update: str, db: Session = Depends(database.get_db), admin: models.User = Depends(auth_utils.get_admin_user)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.status = status_update
    db.commit()
    db.refresh(user)
    return user
