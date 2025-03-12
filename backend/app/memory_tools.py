from google.genai import types
from .memory_db import memory_db
from .database import SessionLocal
from .dependencies import get_from_user_id
from datetime import datetime

# --- Function Declarations for Gemini ---

store_memory_declaration = types.FunctionDeclaration(
    name="store_memory",
    description="Store a user's personal information. You MUST use this tool whenever the user asks you to remember something. Invoke this function for EACH piece of information separately - do not aggregate information.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "content": types.Schema(
                type=types.Type.STRING, 
                description="The exact content to store (e.g., 'the WiFi password is 12345'). Include ALL relevant details."
            ),
            "category": types.Schema(
                type=types.Type.STRING,
                description="The category of information (e.g., 'password', 'birthday', 'recipe')."
            )
        },
        required=["content"],
    ),
)

retrieve_memory_declaration = types.FunctionDeclaration(
    name="retrieve_memory",
    description="Search for previously stored information. You MUST use this tool whenever the user asks for information that might have been stored before. Based on the conversation context, automatically invent and formulate the most relevant search query even if the user hasn't explicitly mentioned what to search for.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "query": types.Schema(
                type=types.Type.STRING, 
                description="The search query you inferred from the conversation context (e.g., if the user asks 'what was the password?', you can infer 'WiFi password' or other relevant passwords)."
            ),
            "limit": types.Schema(
                type=types.Type.INTEGER,
                description="Maximum number of results to return."
            ),
        },
        required=["query"],
    ),
)

update_memory_declaration = types.FunctionDeclaration(
    name="update_memory",
    description="Update previously stored information. You MUST use this tool when the user asks to change or update information that was previously stored.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "query": types.Schema(
                type=types.Type.STRING, 
                description="Query to find the information to update (e.g., 'WiFi password'). Be as specific as possible."
            ),
            "new_content": types.Schema(
                type=types.Type.STRING,
                description="The complete new content to store with ALL relevant details."
            )
        },
        required=["query", "new_content"],
    ),
)

delete_memory_declaration = types.FunctionDeclaration(
    name="delete_memory",
    description="Delete stored information. You MUST use this tool when the user asks to delete or remove previously stored information.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "query": types.Schema(
                type=types.Type.STRING, 
                description="Query to find the information to delete (e.g., 'WiFi password'). Be as specific as possible."
            ),
            "forceDelete": types.Schema(
                type=types.Type.BOOLEAN,
                description="If True, the first result will be deleted. If False, in case of ambiguity, the user will be asked to be more specific. use True or False, is case sensitive."
            )
        },
        required=["query"],
    ),
)

get_user_memories_declaration = types.FunctionDeclaration(
    name="get_user_memories",
    description="Retrieve all memories for a user. Use this tool when the user wants a complete listing of their stored information.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "limit": types.Schema(
                type=types.Type.INTEGER,
                description="Maximum number of memories to return."
            ),
        },
        required=[],
    ),
)

delete_memories_batch_declaration = types.FunctionDeclaration(
    name="delete_memories_batch",
    description="Delete multiple memories at once. Use this tool when the user wants to delete several stored memories by their IDs.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "memory_ids": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(type=types.Type.STRING),
                description="List of memory IDs to delete."
            ),
        },
        required=["memory_ids"],
    ),
)

# --- Tool implementations ---
def delete_memories_batch_tool(user_id: int | str, memory_ids: list) -> dict:
    """Delete multiple memories by their IDs."""
    print(f"Deleting batch of memories for user {user_id}: {memory_ids}")
    
    # Get a DB session
    db = SessionLocal()
    try:
        # Use dependencies.py to get the correct user
        user = get_from_user_id(db, user_id)
        if not user:
            return {
                "status": "error",
                "message": "User not found or invalid"
            }
        
        results = {
            "successful": [],
            "failed": [],
            "not_found": [],
            "unauthorized": []
        }
        
        for memory_id in memory_ids:
            # Check if the memory exists
            memory = memory_db.get_memory(memory_id)
            
            if not memory:
                results["not_found"].append(memory_id)
                continue
            
            # Verify ownership
            if memory["metadata"].get("user_id") != str(user.id):
                results["unauthorized"].append(memory_id)
                continue
            
            # Try to delete the memory
            delete_result = memory_db.delete_memory(
                memory_id=memory_id,
                user_id=user.id
            )
            
            if delete_result:
                # Store successful deletion info
                results["successful"].append({
                    "id": memory_id,
                    "content": memory["content"],
                    "metadata": {
                        "created_at": memory["metadata"].get("created_at", "unknown"),
                        "category": memory["metadata"].get("category", "")
                    }
                })
            else:
                results["failed"].append(memory_id)
        
        # Create a summary for the response
        total = len(memory_ids)
        successful = len(results["successful"])
        
        return {
            "status": "success",
            "message": f"Deleted {successful} out of {total} memories",
            "summary": {
                "total": total,
                "successful": successful,
                "failed": len(results["failed"]),
                "not_found": len(results["not_found"]),
                "unauthorized": len(results["unauthorized"])
            },
            "details": results
        }
    finally:
        db.close()

def store_memory_tool(user_id: int | str, content: str, category: str = None) -> dict:
    """Store a user's personal information."""
    print(f"Storing for user {user_id}: {content}")
    
    # Get a DB session
    db = SessionLocal()
    try:
        # Use dependencies.py to get the correct user
        user = get_from_user_id(db, user_id)
        if not user:
            return {
                "status": "error",
                "message": "User not found or invalid"
            }
        
        # Prepare metadata
        metadata = {
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        if category:
            metadata["category"] = category
        
        # Use memory_db with the correct user ID
        memory_id = memory_db.add_memory(
            content=content, 
            metadata=metadata, 
            user_id=user.id
        )
        
        if not memory_id:
            return {
                "status": "error",
                "message": "Failed to store the information"
            }
        
        return {
            "status": "success",
            "message": f"I've stored: {content}",
            "memory_id": memory_id
        }
    finally:
        db.close()

def retrieve_memory_tool(user_id: int | str, query: str, limit: int = 3) -> dict:
    """Search for previously stored information."""
    print(f"Searching for user {user_id}: {query}")
    
    # Get a DB session
    db = SessionLocal()
    try:
        # Use dependencies.py to get the correct user
        user = get_from_user_id(db, user_id)
        if not user:
            return {
                "status": "error",
                "message": "User not found or invalid"
            }
        
        where_condition = {"user_id": str(user.id)}
        
        # Search in the database with the correct user ID
        results = memory_db.search_memory(
            query=query, 
            user_id=user.id, 
            limit=limit,
            where_condition=where_condition
        )
        
        if not results["documents"]:
            return {
                "status": "not_found",
                "message": "I couldn't find any information related to your request."
            }
        
        # Extract metadata
        memory_metadatas = []
        for idx, memory_id in enumerate(results["ids"]):
            memory = memory_db.get_memory(memory_id)
            if memory:
                memory_metadatas.append({
                    "created_at": memory["metadata"].get("created_at", "unknown"),
                    "updated_at": memory["metadata"].get("updated_at", "unknown"),
                    "category": memory["metadata"].get("category", "")
                })
            else:
                memory_metadatas.append({})
        
        return {
            "status": "success",
            "results": results["documents"],
            "memory_ids": results["ids"],
            "metadata": memory_metadatas
        }
    finally:
        db.close()

def update_memory_tool(user_id: int | str, query: str, new_content: str) -> dict:
    """Update previously stored information."""
    print(f"Updating for user {user_id}: {query} -> {new_content}")
    
    # Get a DB session
    db = SessionLocal()
    try:
        # Use dependencies.py to get the correct user
        user = get_from_user_id(db, user_id)
        if not user:
            return {
                "status": "error",
                "message": "User not found or invalid"
            }
        
        # Search for results to check ambiguity
        results = memory_db.search_memory(
            query=query, 
            user_id=user.id, 
            limit=3
        )
        
        if not results["documents"]:
            return {
                "status": "not_found",
                "message": "I couldn't find the information to update."
            }
        
        # Check for ambiguity (multiple results with similar scores)
        if len(results["documents"]) > 1 and results["distances"][0] > 0.7 * results["distances"][1]:
            # Build a message with options
            options = "\n".join([f"- {doc}" for doc in results["documents"][:3]])
            return {
                "status": "ambiguous",
                "message": f"I found multiple possible matches for '{query}':\n{options}\nCould you be more specific about which information you want to update?"
            }
        
        # If no ambiguity, proceed with the update
        memory_id = results["ids"][0]
        old_content = results["documents"][0]
        
        # Get existing metadata
        existing_memory = memory_db.get_memory(memory_id)
        existing_metadata = existing_memory["metadata"] if existing_memory else {}
        
        # Update metadata
        updated_metadata = existing_metadata.copy()
        updated_metadata["updated_at"] = datetime.now().isoformat()
        
        # Update the database with the correct user ID
        result = memory_db.update_memory(
            memory_id=memory_id, 
            new_content=new_content,
            metadata=updated_metadata,
            user_id=user.id
        )
        
        if not result:
            return {
                "status": "error",
                "message": "Failed to update the information."
            }
        
        return {
            "status": "success",
            "message": f"I've updated the information.",
            "old_content": old_content,
            "new_content": new_content,
            "updated_at": updated_metadata["updated_at"]
        }
    finally:
        db.close()

def delete_memory_tool(user_id: int | str, query: str, forceDelete: bool = False) -> dict:
    """Delete stored information."""
    print(f"Deleting for user {user_id}: {query}")
    
    # Get a DB session
    db = SessionLocal()
    try:
        # Use dependencies.py to get the correct user
        user = get_from_user_id(db, user_id)
        if not user:
            return {
                "status": "error",
                "message": "User not found or invalid"
            }
        
        # Prepare additional filters
        where_condition = {"user_id": str(user.id)}
        
        # Search for results to check for ambiguity
        results = memory_db.search_memory(
            query=query, 
            user_id=user.id, 
            limit=3,
            where_condition=where_condition
        )
        
        print("Results:", results)
        
        if not results["documents"]:
            return {
                "status": "not_found",
                "message": "I couldn't find the information to delete."
            }
        
        print("forceDelete:", forceDelete)
        if not forceDelete:
            # Check for ambiguity (multiple results with similar scores)
            if len(results["documents"]) > 1 and results["distances"][0] > 0.7 * results["distances"][1]:
                # Build a message with options
                options = "\n".join([f"- {doc}" for doc in results["documents"][:3]])
                return {
                    "status": "ambiguous",
                    "message": f"I found multiple possible matches for '{query}':\n{options}\nCould you be more specific about which information you want to delete?"
                }
        
        # If no ambiguity, proceed with deletion
        memory_id = results["ids"][0]
        content = results["documents"][0]
        
        # Get metadata before deletion
        memory = memory_db.get_memory(memory_id)
        print("Memory:", memory)
        metadata = memory["metadata"] if memory else {}
        print("Metadata:", metadata)
        # Delete from database with the correct user ID
        result = memory_db.delete_memory(
            memory_id=memory_id, 
            user_id=user.id
        )
        
        print("final Result:", result)
        
        if not result:
            return {
                "status": "error",
                "message": "Failed to delete the information."
            }
        
        return {
            "status": "success",
            "message": f"I've deleted the information: {content}",
            "metadata": {
                "created_at": metadata.get("created_at", "unknown"),
                "category": metadata.get("category", "")
            }
        }
    finally:
        db.close()

def get_user_memories_tool(user_id: int | str, limit: int = 100) -> dict:
    """Get all memories for a user."""
    print(f"Getting all memories for user {user_id}")
    
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
        
        # Get all memories
        results = memory_db.get_user_memories(
            user_id=user.id,
            limit=limit
        )
        
        if not results["documents"]:
            return {
                "status": "not_found",
                "message": "You don't have any stored memories yet."
            }
        
        # Organize results by category
        memories_by_category = {}
        for idx, doc in enumerate(results["documents"]):
            metadata = results["metadatas"][idx] if idx < len(results["metadatas"]) else {}
            category = metadata.get("category", "General")
            
            if category not in memories_by_category:
                memories_by_category[category] = []
            
            memories_by_category[category].append({
                "content": doc,
                "id": results["ids"][idx] if idx < len(results["ids"]) else None,
                "created_at": metadata.get("created_at", "unknown"),
                "updated_at": metadata.get("updated_at", "unknown")
            })
        
        return {
            "status": "success",
            "count": len(results["documents"]),
            "categories": memories_by_category
        }
    finally:
        db.close()
