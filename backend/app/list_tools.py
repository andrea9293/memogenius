from typing import Dict, Any, List
from .database import SessionLocal
from . import models, schemas, lists
from .dependencies import get_from_user_id

def get_user_id_from_identifier(db, identifier: int | str) -> int:
    """Converts telegram_id or web_token to the database user id"""
    user = get_from_user_id(db, identifier)
    return user.id if user else None

def get_list_tool(user_id: int | str, list_type: str) -> Dict[str, Any]:
    """Get one of the user's lists (todo or shopping) with all its items."""
    print(f"Fetching {list_type} list for user: {user_id}")
    db = SessionLocal()
    try:
        real_user_id = get_user_id_from_identifier(db, user_id)
        if not real_user_id:
            return {"error": "User not found"}
            
        if list_type not in ["todo", "shopping"]:
            return {"error": "Invalid list type. Use 'todo' or 'shopping'."}
        
        # Ensure lists exist
        lists.ensure_user_lists_exist(db, real_user_id)
        
        # Get list with items
        result = lists.get_list_with_items(db, real_user_id, list_type)
        
        if not result:
            return {"error": "Failed to retrieve list"}
            
        # Convert to serializable format
        serialized_result = {
            "id": result["id"],
            "title": result["title"],
            "type": result["type"],
            "user_id": result["user_id"],
            "created_at": result["created_at"].isoformat(),
            "updated_at": result["updated_at"].isoformat() if result["updated_at"] else None,
            "items": [
                {
                    "id": item.id,
                    "text": item.text,
                    "completed": item.completed,
                    "created_at": item.created_at.isoformat(),
                    "updated_at": item.updated_at.isoformat() if item.updated_at else None
                }
                for item in result["items"]
            ]
        }
        
        return serialized_result
    finally:
        db.close()

def update_list_title_tool(user_id: int | str, list_type: str, title: str) -> Dict[str, Any]:
    """Update the title of one of user's lists."""
    print(f"Updating title of {list_type} list for user: {user_id}")
    db = SessionLocal()
    try:
        real_user_id = get_user_id_from_identifier(db, user_id)
        if not real_user_id:
            return {"error": "User not found"}
            
        if list_type not in ["todo", "shopping"]:
            return {"error": "Invalid list type. Use 'todo' or 'shopping'."}
        
        # Ensure lists exist
        lists.ensure_user_lists_exist(db, real_user_id)
        
        # Update the title
        result = lists.update_list_title(db, real_user_id, list_type, title)
        
        if not result:
            return {"error": "Failed to update list title"}
            
        return {
            "id": result.id,
            "title": result.title,
            "type": result.type,
            "user_id": result.user_id,
            "created_at": result.created_at.isoformat(),
            "updated_at": result.updated_at.isoformat() if result.updated_at else None
        }
    finally:
        db.close()

def add_list_item_tool(user_id: int | str, list_type: str, text: str, completed: bool = False) -> Dict[str, Any]:
    """Add an item to one of user's lists."""
    print(f"Adding item to {list_type} list for user: {user_id}")
    db = SessionLocal()
    try:
        real_user_id = get_user_id_from_identifier(db, user_id)
        if not real_user_id:
            return {"error": "User not found"}
            
        if list_type not in ["todo", "shopping"]:
            return {"error": "Invalid list type. Use 'todo' or 'shopping'."}
        
        # Ensure lists exist
        lists.ensure_user_lists_exist(db, real_user_id)
        
        # Create item
        item_data = schemas.ListItemBase(text=text, completed=completed)
        result = lists.create_list_item(db, real_user_id, list_type, item_data)
        
        if not result:
            return {"error": "Failed to add item to list"}
            
        return {
            "id": result.id,
            "list_id": result.list_id,
            "text": result.text,
            "completed": result.completed,
            "created_at": result.created_at.isoformat(),
            "updated_at": result.updated_at.isoformat() if result.updated_at else None
        }
    finally:
        db.close()

def update_list_item_tool(user_id: int | str, item_id: int, text: str = None, completed: bool = None) -> Dict[str, Any]:
    """Update an item in one of user's lists."""
    print(f"Updating item {item_id} for user: {user_id}")
    db = SessionLocal()
    try:
        real_user_id = get_user_id_from_identifier(db, user_id)
        if not real_user_id:
            return {"error": "User not found"}
        
        # Update the item
        item_update = schemas.ListItemUpdate(text=text, completed=completed)
        result = lists.update_list_item(db, item_id, item_update, real_user_id)
        
        if not result:
            return {"error": "Item not found or does not belong to user"}
            
        return {
            "id": result.id,
            "list_id": result.list_id,
            "text": result.text,
            "completed": result.completed,
            "created_at": result.created_at.isoformat(),
            "updated_at": result.updated_at.isoformat() if result.updated_at else None
        }
    finally:
        db.close()

def delete_list_item_tool(user_id: int | str, item_id: int) -> Dict[str, Any]:
    """Delete an item from one of user's lists."""
    print(f"Deleting item {item_id} for user: {user_id}")
    db = SessionLocal()
    try:
        real_user_id = get_user_id_from_identifier(db, user_id)
        if not real_user_id:
            return {"error": "User not found"}
        
        # Get item before deletion to return its details
        item = lists.get_list_item(db, item_id, real_user_id)
        if not item:
            return {"error": "Item not found or does not belong to user"}
            
        # Store item details
        item_data = {
            "id": item.id,
            "list_id": item.list_id,
            "text": item.text,
            "completed": item.completed
        }
        
        # Delete the item
        lists.delete_list_item(db, item_id, real_user_id)
        
        return {
            **item_data,
            "message": "Item successfully deleted"
        }
    finally:
        db.close()

def clear_list_tool(user_id: int | str, list_type: str) -> Dict[str, Any]:
    """Clear all items from one of user's lists."""
    print(f"Clearing all items from {list_type} list for user: {user_id}")
    db = SessionLocal()
    try:
        real_user_id = get_user_id_from_identifier(db, user_id)
        if not real_user_id:
            return {"error": "User not found"}
            
        if list_type not in ["todo", "shopping"]:
            return {"error": "Invalid list type. Use 'todo' or 'shopping'."}
        
        # Ensure lists exist
        lists.ensure_user_lists_exist(db, real_user_id)
        
        # Get list before clearing
        user_list = lists.get_user_list(db, real_user_id, list_type)
        if not user_list:
            return {"error": "List not found"}
            
        # Clear the list
        count = lists.clear_list(db, real_user_id, list_type)
        
        return {
            "id": user_list.id,
            "title": user_list.title,
            "type": user_list.type,
            "cleared_items_count": count,
            "message": f"All items cleared from {user_list.title}"
        }
    finally:
        db.close()

def mark_list_item_completed_tool(user_id: int | str, item_id: int, completed: bool = True) -> Dict[str, Any]:
    """Mark an item as completed or uncompleted in one of user's lists."""
    print(f"Marking item {item_id} as {'completed' if completed else 'uncompleted'} for user: {user_id}")
    # This function is a specialized version of update_list_item_tool
    return update_list_item_tool(user_id, item_id, text=None, completed=completed)
