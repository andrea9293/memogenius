from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from .database import get_db
from . import models

async def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> models.User:
    # Ottieni user_id dai parametri
    user_id = request.query_params.get('user_id')
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="user_id parameter is required"
        )

    # Cerca l'utente prima per telegram_id
    user = db.query(models.User).filter(models.User.telegram_id == user_id).first()
    if user:
        return user

    # Se non trovato, cerca per web_token
    user = db.query(models.User).filter(models.User.web_token == user_id).first()
    if user:
        return user
    
    # Se non trovato, cerca per id
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        return user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="User not found"
    )
