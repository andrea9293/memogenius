from sqlalchemy.orm import Session
from . import models, schemas
from .dependencies import get_from_user_id

def ensure_user_lists_exist(db: Session, user_id: int):
    """Ensures that a user has both a todo list and a shopping list"""
    user = get_from_user_id(db, user_id)
    if not user:
        return False
        
    # Check for Todo list
    todo_list = db.query(models.List).filter(
        models.List.user_id == user.id,
        models.List.type == "todo"
    ).first()
    
    # Create Todo list if it doesn't exist
    if not todo_list:
        todo_list = models.List(
            user_id=user.id,
            title="To-Do List",
            type="todo"
        )
        db.add(todo_list)
        
    # Check for Shopping list
    shopping_list = db.query(models.List).filter(
        models.List.user_id == user.id,
        models.List.type == "shopping"
    ).first()
    
    # Create Shopping list if it doesn't exist
    if not shopping_list:
        shopping_list = models.List(
            user_id=user.id,
            title="Shopping List",
            type="shopping"
        )
        db.add(shopping_list)
        
    db.commit()
    return True

def get_user_list(db: Session, user_id: int, list_type: str):
    """Gets a specific list type for a user"""
    user = get_from_user_id(db, user_id)
    if not user:
        return None
        
    if list_type not in ["todo", "shopping"]:
        return None
        
    return db.query(models.List).filter(
        models.List.user_id == user.id,
        models.List.type == list_type
    ).first()

def update_list_title(db: Session, user_id: int, list_type: str, new_title: str):
    """Updates the title of a user's list"""
    user_list = get_user_list(db, user_id, list_type)
    if not user_list:
        return None
        
    user_list.title = new_title
    db.commit()
    db.refresh(user_list)
    return user_list

def get_list_items(db: Session, user_id: int, list_type: str, skip: int = 0, limit: int = 100):
    """Gets all items in a specific list"""
    user_list = get_user_list(db, user_id, list_type)
    if not user_list:
        return []
        
    return db.query(models.ListItem).filter(
        models.ListItem.list_id == user_list.id
    ).offset(skip).limit(limit).all()

def get_list_with_items(db: Session, user_id: int, list_type: str):
    """Gets a list with all its items"""
    user_list = get_user_list(db, user_id, list_type)
    if not user_list:
        return None
        
    items = get_list_items(db, user_id, list_type)
    
    result = {
        "id": user_list.id,
        "title": user_list.title,
        "type": user_list.type,
        "user_id": user_list.user_id,
        "created_at": user_list.created_at,
        "updated_at": user_list.updated_at,
        "items": items
    }
    
    return result

def create_list_item(db: Session, user_id: int, list_type: str, item: schemas.ListItemBase):
    """Creates a new item in a user's list"""
    user_list = get_user_list(db, user_id, list_type)
    if not user_list:
        return None
        
    db_item = models.ListItem(
        list_id=user_list.id,
        text=item.text,
        completed=item.completed
    )
    
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_list_item(db: Session, item_id: int, user_id: int):
    """Gets a specific list item, ensuring it belongs to the user"""
    user = get_from_user_id(db, user_id)
    if not user:
        return None
        
    return db.query(models.ListItem).join(
        models.List, models.ListItem.list_id == models.List.id
    ).filter(
        models.ListItem.id == item_id,
        models.List.user_id == user.id
    ).first()

def update_list_item(db: Session, item_id: int, item_update: schemas.ListItemUpdate, user_id: int):
    """Updates a list item"""
    db_item = get_list_item(db, item_id, user_id)
    if not db_item:
        return None
        
    if item_update.text is not None:
        db_item.text = item_update.text
    if item_update.completed is not None:
        db_item.completed = item_update.completed
        
    db.commit()
    db.refresh(db_item)
    return db_item

def delete_list_item(db: Session, item_id: int, user_id: int):
    """Deletes a list item"""
    db_item = get_list_item(db, item_id, user_id)
    if not db_item:
        return None
        
    db.delete(db_item)
    db.commit()
    return db_item

def clear_list(db: Session, user_id: int, list_type: str):
    """Removes all items from a list"""
    user_list = get_user_list(db, user_id, list_type)
    if not user_list:
        return 0
        
    count = db.query(models.ListItem).filter(
        models.ListItem.list_id == user_list.id
    ).delete()
    
    db.commit()
    return count
