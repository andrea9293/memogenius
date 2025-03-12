from google.genai import types
from .database import SessionLocal
from .dependencies import get_from_user_id
from datetime import datetime
from sqlalchemy.orm import Session
from . import models, schemas
from typing import Optional, List, Dict, Any

# --- Function Declarations for Gemini ---

get_list_declaration = types.FunctionDeclaration(
    name="get_list",
    description="Retrieves one of the user's lists (todo or shopping) with all its items.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "list_type": types.Schema(
                type=types.Type.STRING,
                description="Type of list to retrieve: 'todo' or 'shopping'.",
            ),
        },
        required=["list_type"],
    ),
)

update_list_title_declaration = types.FunctionDeclaration(
    name="update_list_title",
    description="Updates the title of one of the user's lists.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "list_type": types.Schema(
                type=types.Type.STRING,
                description="Type of list to update: 'todo' or 'shopping'.",
            ),
            "title": types.Schema(
                type=types.Type.STRING,
                description="New title for the list.",
            ),
        },
        required=["list_type", "title"],
    ),
)

clear_list_declaration = types.FunctionDeclaration(
    name="clear_list",
    description="Removes all items from one of the user's lists.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "list_type": types.Schema(
                type=types.Type.STRING,
                description="Type of list to clear: 'todo' or 'shopping'.",
            ),
        },
        required=["list_type"],
    ),
)

add_list_item_declaration = types.FunctionDeclaration(
    name="add_list_item",
    description="Adds a new item to one of the user's lists.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "list_type": types.Schema(
                type=types.Type.STRING,
                description="Type of list to add to: 'todo' or 'shopping'.",
            ),
            "text": types.Schema(
                type=types.Type.STRING,
                description="Text content of the item.",
            ),
            "completed": types.Schema(
                type=types.Type.BOOLEAN,
                description="Whether the item is completed (default: false).",
            ),
        },
        required=["list_type", "text"],
    ),
)

update_list_item_declaration = types.FunctionDeclaration(
    name="update_list_item",
    description="Updates an existing item in one of the user's lists.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "item_id": types.Schema(
                type=types.Type.INTEGER,
                description="ID of the item to update.",
            ),
            "text": types.Schema(
                type=types.Type.STRING,
                description="New text content for the item.",
            ),
            "completed": types.Schema(
                type=types.Type.BOOLEAN,
                description="New completion status for the item.",
            ),
        },
        required=["item_id"],
    ),
)

delete_list_item_declaration = types.FunctionDeclaration(
    name="delete_list_item",
    description="Removes an item from one of the user's lists.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "item_id": types.Schema(
                type=types.Type.INTEGER,
                description="ID of the item to delete.",
            ),
        },
        required=["item_id"],
    ),
)

mark_list_item_completed_declaration = types.FunctionDeclaration(
    name="mark_list_item_completed",
    description="Marks an item as completed or uncompleted.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "item_id": types.Schema(
                type=types.Type.INTEGER,
                description="ID of the item to mark.",
            ),
            "completed": types.Schema(
                type=types.Type.BOOLEAN,
                description="Whether to mark as completed (true) or uncompleted (false). Default is true.",
            ),
        },
        required=["item_id"],
    ),
)

# --- Helper functions ---

def get_or_create_list(db: Session, user_id: int, list_type: str) -> models.List:
    """Gets an existing list or creates it if it doesn't exist."""
    if list_type not in ['todo', 'shopping']:
        raise ValueError("List type must be 'todo' or 'shopping'")
    
    # Try to get existing list - CORRETTO QUI: list_type -> type
    db_list = db.query(models.List).filter(
        models.List.user_id == user_id,
        models.List.type == list_type
    ).first()
    
    # Create if it doesn't exist
    if not db_list:
        default_title = "To-Do List" if list_type == "todo" else "Shopping List"
        db_list = models.List(
            user_id=user_id,
            type=list_type,
            title=default_title,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.add(db_list)
        db.commit()
        db.refresh(db_list)
    
    return db_list

# --- Tool implementations ---

def get_list_tool(user_id: int | str, list_type: str) -> Dict[str, Any]:
    """Retrieves one of the user's lists with all its items."""
    print(f"Getting {list_type} list for user {user_id}")
    
    # Get a DB session
    db = SessionLocal()
    try:
        # Get the correct user
        user = get_from_user_id(db, user_id)
        if not user:
            return {
                "status": "error",
                "message": "User not found or invalid"
            }
        
        try:
            # Get or create the list
            db_list = get_or_create_list(db, user.id, list_type)
            
            # Get list items
            items = db.query(models.ListItem).filter(
                models.ListItem.list_id == db_list.id
            ).order_by(models.ListItem.created_at).all()
            
            # Format the result
            formatted_items = []
            for item in items:
                formatted_items.append({
                    "id": item.id,
                    "text": item.text,
                    "completed": item.completed,
                    "created_at": item.created_at.isoformat(),
                    "updated_at": item.updated_at.isoformat() if item.updated_at else None
                })
            
            return {
                "status": "success",
                "list": {
                    "id": db_list.id,
                    "title": db_list.title,
                    "type": db_list.type,
                    "created_at": db_list.created_at.isoformat(),
                    "updated_at": db_list.updated_at.isoformat() if db_list.updated_at else None,
                    "items": formatted_items,
                    "item_count": len(formatted_items),
                    "completed_count": sum(1 for item in formatted_items if item["completed"])
                }
            }
        except ValueError as e:
            return {
                "status": "error",
                "message": str(e)
            }
    finally:
        db.close()

def update_list_title_tool(user_id: int | str, list_type: str, title: str) -> Dict[str, Any]:
    """Updates the title of one of the user's lists."""
    print(f"Updating title of {list_type} list for user {user_id}")
    
    # Get a DB session
    db = SessionLocal()
    try:
        # Get the correct user
        user = get_from_user_id(db, user_id)
        if not user:
            return {
                "status": "error",
                "message": "User not found or invalid"
            }
        
        try:
            # Get or create the list
            db_list = get_or_create_list(db, user.id, list_type)
            
            # Update the title
            old_title = db_list.title
            db_list.title = title
            db_list.updated_at = datetime.now()
            
            db.commit()
            db.refresh(db_list)
            
            return {
                "status": "success",
                "message": f"List title updated from '{old_title}' to '{title}'",
                "list": {
                    "id": db_list.id,
                    "title": db_list.title,
                    "type": db_list.type
                }
            }
        except ValueError as e:
            return {
                "status": "error",
                "message": str(e)
            }
    finally:
        db.close()

def clear_list_tool(user_id: int | str, list_type: str) -> Dict[str, Any]:
    """Removes all items from one of the user's lists."""
    print(f"Clearing {list_type} list for user {user_id}")
    
    # Get a DB session
    db = SessionLocal()
    try:
        # Get the correct user
        user = get_from_user_id(db, user_id)
        if not user:
            return {
                "status": "error",
                "message": "User not found or invalid"
            }
        
        try:
            # Get or create the list
            db_list = get_or_create_list(db, user.id, list_type)
            
            # Get item count before deletion
            item_count = db.query(models.ListItem).filter(
                models.ListItem.list_id == db_list.id
            ).count()
            
            # Delete all items
            db.query(models.ListItem).filter(
                models.ListItem.list_id == db_list.id
            ).delete()
            
            # Update list
            db_list.updated_at = datetime.now()
            db.commit()
            
            return {
                "status": "success",
                "message": f"Removed {item_count} items from the {list_type} list",
                "list": {
                    "id": db_list.id,
                    "title": db_list.title,
                    "type": db_list.type,
                    "items_removed": item_count
                }
            }
        except ValueError as e:
            return {
                "status": "error",
                "message": str(e)
            }
    finally:
        db.close()

def add_list_item_tool(user_id: int | str, list_type: str, text: str, completed: bool = False) -> Dict[str, Any]:
    """Adds a new item to one of the user's lists."""
    print(f"Adding item to {list_type} list for user {user_id}: {text}")
    
    # Get a DB session
    db = SessionLocal()
    try:
        # Get the correct user
        user = get_from_user_id(db, user_id)
        if not user:
            return {
                "status": "error",
                "message": "User not found or invalid"
            }
        
        try:
            # Get or create the list
            db_list = get_or_create_list(db, user.id, list_type)
            
            # Create new item
            new_item = models.ListItem(
                list_id=db_list.id,
                text=text,
                completed=completed,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            db.add(new_item)
            db.commit()
            db.refresh(new_item)
            
            # Update list last modified time
            db_list.updated_at = datetime.now()
            db.commit()
            
            return {
                "status": "success",
                "message": f"Added '{text}' to the {list_type} list",
                "item": {
                    "id": new_item.id,
                    "text": new_item.text,
                    "completed": new_item.completed,
                    "created_at": new_item.created_at.isoformat()
                },
                "list": {
                    "id": db_list.id,
                    "title": db_list.title,
                    "type": db_list.type
                }
            }
        except ValueError as e:
            return {
                "status": "error",
                "message": str(e)
            }
    finally:
        db.close()

def update_list_item_tool(user_id: int | str, item_id: int, text: Optional[str] = None, completed: Optional[bool] = None) -> Dict[str, Any]:
    """Updates an existing item in one of the user's lists."""
    print(f"Updating list item {item_id} for user {user_id}")
    
    # Get a DB session
    db = SessionLocal()
    try:
        # Get the correct user
        user = get_from_user_id(db, user_id)
        if not user:
            return {
                "status": "error",
                "message": "User not found or invalid"
            }
        
        # Get the item - CORRETTO QUI: aggiunto join esplicito
        item = db.query(models.ListItem).join(
            models.List, 
            models.ListItem.list_id == models.List.id
        ).filter(
            models.ListItem.id == item_id,
            models.List.user_id == user.id
        ).first()
        
        if not item:
            return {
                "status": "error",
                "message": f"Item with ID {item_id} not found or doesn't belong to this user"
            }
        
        # Track old values for response
        old_text = item.text
        old_completed = item.completed
        
        # Update item fields
        if text is not None:
            item.text = text
        
        if completed is not None:
            item.completed = completed
        
        item.updated_at = datetime.now()
        
        # Update list last modified time
        db_list = db.query(models.List).filter(models.List.id == item.list_id).first()
        if db_list:
            db_list.updated_at = datetime.now()
        
        db.commit()
        db.refresh(item)
        
        return {
            "status": "success",
            "message": "Item updated successfully",
            "item": {
                "id": item.id,
                "text": item.text,
                "completed": item.completed,
                "old_text": old_text,
                "old_completed": old_completed,
                "updated_at": item.updated_at.isoformat()
            }
        }
    finally:
        db.close()

def delete_list_item_tool(user_id: int | str, item_id: int) -> Dict[str, Any]:
    """Removes an item from one of the user's lists."""
    print(f"Deleting list item {item_id} for user {user_id}")
    
    # Get a DB session
    db = SessionLocal()
    try:
        # Get the correct user
        user = get_from_user_id(db, user_id)
        if not user:
            return {
                "status": "error",
                "message": "User not found or invalid"
            }
        
        # Get the item with list info - CORRETTO QUI: aggiunto join esplicito
        item = db.query(models.ListItem).join(
            models.List, 
            models.ListItem.list_id == models.List.id
        ).filter(
            models.ListItem.id == item_id,
            models.List.user_id == user.id
        ).first()
        
        if not item:
            return {
                "status": "error",
                "message": f"Item with ID {item_id} not found or doesn't belong to this user"
            }
        
        # Store info for response
        item_text = item.text
        list_id = item.list_id
        
        # Delete the item
        db.delete(item)
        
        # Update list last modified time
        db_list = db.query(models.List).filter(models.List.id == list_id).first()
        if db_list:
            db_list.updated_at = datetime.now()
        
        db.commit()
        
        return {
            "status": "success",
            "message": f"Deleted item: {item_text}",
            "item": {
                "id": item_id,
                "text": item_text
            }
        }
    finally:
        db.close()

def mark_list_item_completed_tool(user_id: int | str, item_id: int, completed: bool = True) -> Dict[str, Any]:
    """Marks an item as completed or uncompleted."""
    print(f"Marking list item {item_id} as {'completed' if completed else 'not completed'} for user {user_id}")
    
    # Get a DB session
    db = SessionLocal()
    try:
        # Get the correct user
        user = get_from_user_id(db, user_id)
        if not user:
            return {
                "status": "error",
                "message": "User not found or invalid"
            }
        
        # Get the item - CORRETTO QUI: aggiunto join esplicito
        item = db.query(models.ListItem).join(
            models.List, 
            models.ListItem.list_id == models.List.id
        ).filter(
            models.ListItem.id == item_id,
            models.List.user_id == user.id
        ).first()
        
        if not item:
            return {
                "status": "error",
                "message": f"Item with ID {item_id} not found or doesn't belong to this user"
            }
        
        # Update completion status
        old_status = item.completed
        item.completed = completed
        item.updated_at = datetime.now()
        
        # Update list last modified time
        db_list = db.query(models.List).filter(models.List.id == item.list_id).first()
        if db_list:
            db_list.updated_at = datetime.now()
        
        db.commit()
        db.refresh(item)
        
        status_message = "completed" if completed else "marked as incomplete"
        
        return {
            "status": "success",
            "message": f"Item '{item.text}' {status_message}",
            "item": {
                "id": item.id,
                "text": item.text,
                "completed": item.completed,
                "previous_status": old_status,
                "updated_at": item.updated_at.isoformat()
            }
        }
    finally:
        db.close()
