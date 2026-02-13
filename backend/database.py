from pymongo import MongoClient
import os
from bson.objectid import ObjectId
from datetime import datetime

# --- MongoDB Configuration ---
# Fallback URI if environment variable is not set
HARDCODED_URI = "mongodb+srv://RaghaviSai123:Raghavi123@cluster0.aydji1p.mongodb.net/social_anxiety_db?retryWrites=true&w=majority"

# Use environment variable first, fallback to hardcoded
MONGODB_URI = os.getenv("MONGODB_URI", HARDCODED_URI)
DB_NAME = "social_anxiety_db"
COLLECTION_NAME = "chat_collection"

# Initialize client and collection
chats_collection = None

try:
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
    # Trigger connection error if URI is invalid
    client.server_info()
    
    db = client[DB_NAME]
    chats_collection = db[COLLECTION_NAME]
    print(f"MongoDB connection successful: {DB_NAME}.{COLLECTION_NAME}")
except Exception as e:
    print(f"MongoDB connection failed: {e}")
    chats_collection = None

# --- Helper Functions ---

def chat_helper(chat) -> dict:
    """
    Converts MongoDB document to JSON-serializable dictionary.
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

def insert_chat(chat_entry: dict) -> bool:
    """
    Inserts a chat entry into the collection.
    Returns True if successful, False otherwise.
    """
    try:
        if chats_collection is not None:
            result = chats_collection.insert_one(chat_entry)
            print(f"Inserted chat with id: {result.inserted_id}")
            return True
        else:
            print("chats_collection is None. Cannot insert data.")
            return False
    except Exception as e:
        print(f"Error inserting chat: {e}")
        return False

def delete_chat(chat_id: str) -> bool:
    """
    Deletes a chat message by its ID.
    """
    try:
        if chats_collection is not None:
            result = chats_collection.delete_one({"_id": ObjectId(chat_id)})
            if result.deleted_count > 0:
                print(f"Deleted chat with id: {chat_id}")
                return True
            else:
                print(f"No chat found with id: {chat_id}")
                return False
        else:
            print("chats_collection is None. Cannot delete data.")
            return False
    except Exception as e:
        print(f"Error deleting chat: {e}")
        return False

def get_all_chats() -> list:
    """
    Retrieves all chats from the collection.
    """
    try:
        if chats_collection is not None:
            chats = list(chats_collection.find().sort("timestamp", -1))
            return [chat_helper(chat) for chat in chats]
        else:
            print("chats_collection is None. Cannot fetch data.")
            return []
    except Exception as e:
        print(f"Error fetching chats: {e}")
        return []
