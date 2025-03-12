import os
import chromadb
from chromadb.config import Settings
from google import genai
from .config import settings
import json
import threading
from datetime import datetime

# Global variable for singleton instance
_memory_db = None
# Lock for thread-safe initialization
_init_lock = threading.Lock()

class MemoryDB:
    def __init__(self):
        """Initializes ChromaDB and the Gemini client for embeddings."""        
        # Make sure the directory exists
        os.makedirs(settings.CUSTOM_RAG_PATH, exist_ok=True)
        
        # Initialize the ChromaDB client
        self.client = chromadb.PersistentClient(
            path=settings.CUSTOM_RAG_PATH,
            settings=Settings(allow_reset=True)
        )
        
        # Initialize the Gemini client for embeddings
        self.gemini_client = genai.Client(api_key=settings.GEMINI_API_KEY)
        
        # Create or get the collection
        try:
            self.collection = self.client.get_collection("user_memories")
        except:
            print("Creating new 'user_memories' collection for RAG")
            self.collection = self.client.create_collection(
                name="user_memories",
                metadata={"hnsw:space": "cosine"}
            )
    
    def create_embedding(self, content):
        """Creates an embedding for the provided content using Gemini."""
        try:
            response = self.gemini_client.models.embed_content(
                model='text-embedding-004',
                contents=[content]
            )
            # Extract numerical values from ContentEmbedding object
            return response.embeddings[0].values
        except Exception as e:
            print(f"Error creating embedding: {e}")
            # Return an empty embedding in case of error
            return []
    
    def add_memory(self, content, metadata=None, user_id=None):
        """
        Adds a new memory to the database.
        
        Args:
            content: The content to store
            metadata: Additional metadata (optional)
            user_id: ID of the user who owns the memory
        
        Returns:
            memory_id: The ID of the saved memory or None in case of error
        """
        try:
            # Create an ID for the memory
            memory_id = f"memory_{user_id}_{hash(content)}"
            
            # Create the embedding
            embedding = self.create_embedding(content)
            if not embedding:
                return None
            
            # Prepare metadata
            if metadata is None:
                metadata = {}
                
            # Add timestamps if not already present
            if "created_at" not in metadata:
                metadata["created_at"] = datetime.now().isoformat()
            if "updated_at" not in metadata:
                metadata["updated_at"] = datetime.now().isoformat()
                
            if user_id:
                metadata["user_id"] = str(user_id)
            
            # Add to collection
            self.collection.add(
                ids=[memory_id],
                embeddings=[embedding],
                documents=[content],
                metadatas=[metadata]
            )
            
            return memory_id
        except Exception as e:
            print(f"Error adding memory: {e}")
            return None
    
    def search_memory(self, query, user_id=None, limit=3, where_condition=None):
        """
        Searches for memories similar to the query.
        
        Args:
            query: The search query
            user_id: User ID (optional)
            limit: Maximum number of results
            where_condition: Additional filtering conditions (optional)
            
        Returns:
            Dict with IDs, documents and distances
        """
        try:
            # Create the embedding for the query
            query_embedding = self.create_embedding(query)
            if not query_embedding:
                return {"ids": [], "documents": [], "distances": []}
            
            # Prepare filter conditions
            if where_condition is None:
                where_condition = {}
                
            if user_id and "user_id" not in where_condition:
                where_condition["user_id"] = str(user_id)
            
            # Search in the collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                where=where_condition if where_condition else None
            )
            
            return {
                "ids": results["ids"][0] if results["ids"] else [],
                "documents": results["documents"][0] if results["documents"] else [],
                "distances": results["distances"][0] if results["distances"] else [],
                "metadatas": results["metadatas"][0] if "metadatas" in results and results["metadatas"] else []
            }
        except Exception as e:
            print(f"Error searching memory: {e}")
            return {"ids": [], "documents": [], "distances": [], "metadatas": []}
    
    def get_memory(self, memory_id):
        """Gets a specific memory by ID."""
        try:
            result = self.collection.get(ids=[memory_id])
            print("Result get_memory:", result)
            if result["ids"]:
                # Gestisci correttamente il caso in cui embeddings è None
                embeddings_value = result.get("embeddings", None)
                embedding = embeddings_value[0] if embeddings_value is not None else []
                
                return {
                    "id": result["ids"][0],
                    "content": result["documents"][0],
                    "metadata": result["metadatas"][0],
                    "embedding": embedding
                }
            return None
        except Exception as e:
            print(f"Error getting memory: {e}")
            return None
    
    def update_memory(self, memory_id, new_content, metadata=None, user_id=None):
        """
        Updates an existing memory.
        
        Args:
            memory_id: ID of the memory to update
            new_content: New content
            metadata: New metadata (optional)
            user_id: User ID for ownership verification (optional)
            
        Returns:
            memory_id on success, None otherwise
        """
        try:
            # Check if the memory exists
            existing = self.get_memory(memory_id)
            if not existing:
                return None
            
            # Verify ownership if user_id is specified
            if user_id and existing["metadata"].get("user_id") != str(user_id):
                return None
            
            # Create the new embedding
            new_embedding = self.create_embedding(new_content)
            if not new_embedding:
                return None
            
            # Prepare the metadata
            if metadata is None:
                metadata = existing["metadata"].copy()
            
            # Preserve existing metadata fields if not provided in the new metadata
            if "created_at" not in metadata and "created_at" in existing["metadata"]:
                metadata["created_at"] = existing["metadata"]["created_at"]
            
            # Always update the updated_at timestamp
            metadata["updated_at"] = datetime.now().isoformat()
                
            if user_id:
                metadata["user_id"] = str(user_id)
            
            # Update the collection
            self.collection.update(
                ids=[memory_id],
                embeddings=[new_embedding],
                documents=[new_content],
                metadatas=[metadata]
            )
            
            return memory_id
        except Exception as e:
            print(f"Error updating memory: {e}")
            return None
    
    def delete_memory(self, memory_id, user_id=None):
        """
        Deletes a memory from the database.
        
        Args:
            memory_id: ID of the memory to delete
            user_id: User ID for ownership verification (optional)
            
        Returns:
            True if successfully deleted, False otherwise
        """
        try:
            # Check if the memory exists
            existing = self.get_memory(memory_id)
            if not existing:
                return False
            
            # Verify ownership if user_id is specified
            if user_id and existing["metadata"].get("user_id") != str(user_id):
                return False
            
            # Delete from the collection
            self.collection.delete(ids=[memory_id])
            return True
        except Exception as e:
            print(f"Error deleting memory: {e}")
            return False
    
    def get_user_memories(self, user_id, limit=100):
        """
        Get all memories for a specific user.
        
        Args:
            user_id: User ID
            limit: Maximum number of results
            
        Returns:
            Dict with IDs, documents and metadata
        """
        try:
            results = self.collection.get(
                where={"user_id": str(user_id)},
                limit=limit
            )
            
            return {
                "ids": results["ids"] if results["ids"] else [],
                "documents": results["documents"] if results["documents"] else [],
                "metadatas": results["metadatas"] if "metadatas" in results else []
            }
        except Exception as e:
            print(f"Error getting user memories: {e}")
            return {"ids": [], "documents": [], "metadatas": []}

def init_memory_db():
    """Initializes and returns the singleton instance of MemoryDB."""
    global _memory_db
    if _memory_db is None:
        with _init_lock:
            if _memory_db is None:  # Double-check under the lock
                _memory_db = MemoryDB()
    return _memory_db

def get_memory_db():
    """Gets the singleton instance of MemoryDB, initializing it if necessary."""
    global _memory_db
    if _memory_db is None:
        _memory_db = init_memory_db()
    return _memory_db

# Initialize the singleton instance immediately
memory_db = get_memory_db()
