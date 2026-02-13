from pymongo import MongoClient
import os
from bson.objectid import ObjectId

# 1. MongoDB Connection
# Check for environment variable first (Best Practice for Vercel)
# Fallback to the hardcoded string if env var is missing (User provided string)
DEFAULT_URI = "mongodb+srv://RaghaviSai123:Raghavi123@cluster0.aydji1p.mongodb.net/social_anxiety_db?retryWrites=true&w=majority"
MONGODB_URI = os.getenv("MONGODB_URI", DEFAULT_URI)

client = MongoClient(MONGODB_URI)

db = client["social_anxiety_db"] 
chats_collection = db["chat_collection"]

# 2. Helper Functions (Required by backend/main.py)

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
        chats_collection.delete_one({"_id": ObjectId(id)})
        return True
    except Exception as e:
        print(f"Error deleting chat: {e}")
        return False
