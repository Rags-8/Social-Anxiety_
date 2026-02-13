from pymongo import MongoClient
import os
from bson.objectid import ObjectId

# User-provided connection URI (used as fallback or default)
# User-provided connection URI (used as fallback or default)
HARDCODED_URI = "mongodb+srv://RaghaviSai123:Raghavi123@cluster0.aydji1p.mongodb.net/social_anxiety_db?appName=Cluster0"

# Correct Logic: Check environment variable first, else use the hardcoded string
MONGODB_URI = os.getenv("MONGODB_URI", HARDCODED_URI)

chats_collection = None

try:
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    db = client["social_anxiety_db"]
    chats_collection = db["chat_collection"]
    print("MongoDB connection successful")
except Exception as e:
    print(f"MongoDB connection failed: {e}")
    chats_collection = None

# --- Helper Functions (Required by backend/main.py) ---
# Added these back because removing them will crash the app (ImportError in main.py)

def chat_helper(chat) -> dict:
    """
    Converts MongoDB document to a JSON-serializable dictionary.
    """
    return {
        "id": str(chat["_id"]),
        "user_id": chat.get("user_id"),
        "message": chat.get("message"),
        "response": chat.get("response"),
        "anxiety_level": chat.get("anxiety_level"),
        "suggestions": chat.get("suggestions"),
        "timestamp": str(chat.get("timestamp"))
    }

def delete_chat(id: str):
    """
    Deletes a chat message by its ID.
    """
    try:
        if chats_collection:
            chats_collection.delete_one({"_id": ObjectId(id)})
            return True
        return False
    except Exception as e:
        print(f"Error deleting chat: {e}")
        return False
