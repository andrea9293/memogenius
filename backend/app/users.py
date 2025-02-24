import random
import string
from sqlalchemy.orm import Session
from . import models
from .models import User

def generate_access_key() -> str:
    """Genera una chiave di accesso nel formato MG-XXXX-XXXX"""
    chars = string.ascii_uppercase + string.digits
    code = ''.join(random.choices(chars, k=8))
    return f"MG-{code[:4]}-{code[4:]}"

def get_or_create_telegram_user(db: Session, telegram_id: int) -> User:
    """Crea o recupera un utente da Telegram ID"""
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        access_key = generate_access_key()
        user = User(telegram_id=telegram_id, access_key=access_key)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

def link_web_token(db: Session, access_key: str, web_token: str) -> User:
    """Collega un web token a un utente esistente"""
    user = db.query(User).filter(User.access_key == access_key).first()
    if user:
        user.web_token = web_token
        db.commit()
        db.refresh(user)
    return user

def get_user_by_token(db: Session, web_token: str) -> User:
    """Recupera un utente dal web token"""
    return db.query(User).filter(User.web_token == web_token).first()
