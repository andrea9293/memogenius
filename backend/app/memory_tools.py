from google.genai import types
from .memory_db import memory_db
from .database import SessionLocal
from .dependencies import get_from_user_id

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
            ),
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
            ),
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
        },
        required=["query"],
    ),
)

# --- Tool implementations ---

def store_memory_tool(user_id: int | str, content: str, category: str = None) -> dict:
    """Store a user's personal information."""
    print(f"Storing for user {user_id}: {content}")
    
    # Ottieni una sessione DB
    db = SessionLocal()
    try:
        # Usa dependencies.py per ottenere l'utente corretto
        user = get_from_user_id(db, user_id)
        if not user:
            return {
                "status": "error",
                "message": "User not found or invalid"
            }
        
        # Prepara i metadati
        metadata = {}
        if category:
            metadata["category"] = category
        
        # Usa il memory_db con l'ID utente corretto
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
    
    # Ottieni una sessione DB
    db = SessionLocal()
    try:
        # Usa dependencies.py per ottenere l'utente corretto
        user = get_from_user_id(db, user_id)
        if not user:
            return {
                "status": "error",
                "message": "User not found or invalid"
            }
        
        # Cerca nel database con l'ID utente corretto
        results = memory_db.search_memory(
            query=query, 
            user_id=user.id, 
            limit=limit
        )
        
        if not results["documents"]:
            return {
                "status": "not_found",
                "message": "I couldn't find any information related to your request."
            }
        
        return {
            "status": "success",
            "results": results["documents"],
            "memory_ids": results["ids"]
        }
    finally:
        db.close()

def update_memory_tool(user_id: int | str, query: str, new_content: str) -> dict:
    """Update previously stored information."""
    print(f"Updating for user {user_id}: {query} -> {new_content}")
    
    # Ottieni una sessione DB
    db = SessionLocal()
    try:
        # Usa dependencies.py per ottenere l'utente corretto
        user = get_from_user_id(db, user_id)
        if not user:
            return {
                "status": "error",
                "message": "User not found or invalid"
            }
        
        # Cerca i risultati per verificare ambiguità
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
        
        # Verifica ambiguità (più risultati con punteggi simili)
        if len(results["documents"]) > 1 and results["distances"][0] > 0.7 * results["distances"][1]:
            # Costruisci un messaggio con le opzioni
            options = "\n".join([f"- {doc}" for doc in results["documents"][:3]])
            return {
                "status": "ambiguous",
                "message": f"I found multiple possible matches for '{query}':\n{options}\nCould you be more specific about which information you want to update?"
            }
        
        # Se non c'è ambiguità, procedi con l'aggiornamento
        memory_id = results["ids"][0]
        old_content = results["documents"][0]
        
        # Aggiorna il database con l'ID utente corretto
        result = memory_db.update_memory(
            memory_id=memory_id, 
            new_content=new_content,
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
            "new_content": new_content
        }
    finally:
        db.close()

def delete_memory_tool(user_id: int | str, query: str) -> dict:
    """Delete stored information."""
    print(f"Deleting for user {user_id}: {query}")
    
    # Ottieni una sessione DB
    db = SessionLocal()
    try:
        # Usa dependencies.py per ottenere l'utente corretto
        user = get_from_user_id(db, user_id)
        if not user:
            return {
                "status": "error",
                "message": "User not found or invalid"
            }
        
        # Cerca i risultati per verificare ambiguità
        results = memory_db.search_memory(
            query=query, 
            user_id=user.id, 
            limit=3
        )
        
        if not results["documents"]:
            return {
                "status": "not_found",
                "message": "I couldn't find the information to delete."
            }
        
        # Verifica ambiguità (più risultati con punteggi simili)
        if len(results["documents"]) > 1 and results["distances"][0] > 0.7 * results["distances"][1]:
            # Costruisci un messaggio con le opzioni
            options = "\n".join([f"- {doc}" for doc in results["documents"][:3]])
            return {
                "status": "ambiguous",
                "message": f"I found multiple possible matches for '{query}':\n{options}\nCould you be more specific about which information you want to delete?"
            }
        
        # Se non c'è ambiguità, procedi con l'eliminazione
        memory_id = results["ids"][0]
        content = results["documents"][0]
        
        # Elimina dal database con l'ID utente corretto
        result = memory_db.delete_memory(
            memory_id=memory_id, 
            user_id=user.id
        )
        
        if not result:
            return {
                "status": "error",
                "message": "Failed to delete the information."
            }
        
        return {
            "status": "success",
            "message": f"I've deleted the information: {content}"
        }
    finally:
        db.close()
