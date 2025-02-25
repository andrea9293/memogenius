from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from .database import get_db
from . import models

def get_from_user_id(db: Session, user_id: int) -> int | None:
    """Gets a user object given their database user_id, telegram_id or web_token"""
    user = db.query(models.User).filter(models.User.telegram_id == user_id).first()
    if user:
        return user

    # If not found, search by web_token
    user = db.query(models.User).filter(models.User.web_token == user_id).first()
    if user:
        return user
    
    # If not found, search by id
    user = db.query(models.User).filter(models.User.id == user_id).first()
    return user
    
async def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> models.User:
    # Get user_id from parameters
    user_id = request.query_params.get('user_id')
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="user_id parameter is required"
        )

    # Search user first by telegram_id
    user = db.query(models.User).filter(models.User.telegram_id == user_id).first()
    if user:
        return user

    # If not found, search by web_token
    user = db.query(models.User).filter(models.User.web_token == user_id).first()
    if user:
        return user
    
    # If not found, search by id
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        return user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="User not found"
    )
