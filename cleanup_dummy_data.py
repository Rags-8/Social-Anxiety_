import certifi
from pymongo import MongoClient
import os

MONGODB_URI = "mongodb+srv://RaghaviSai123:Raghavi123@cluster0.aydji1p.mongodb.net/social_anxiety_db?retryWrites=true&w=majority"
DB_NAME = "social_anxiety_db"
COLLECTION_NAME = "chat_collection"
USER_ID = "guest_streamlit"

DUMMY_MESSAGES = [
    "I feel a bit nervous about the presentation tomorrow.",
    "I panicked when I walked into the crowded room.",
    "I'm worried people are judging me when I eat in public.",
    "Had a great time with friends today, felt unexpected calm.",
    "I don't want to go to the party, I feel sick just thinking about it.",
    "I spoke up in the meeting today and it went okay."
]

def cleanup():
    try:
        print("Connecting to MongoDB...")
        # Exact copy from backend/main.py which is working
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000, tlsCAFile=certifi.where())
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        
        # Verify connection
        client.admin.command('ping')
        print("Connected successfully (verified).")
        
        print(f"Cleaning up dummy data for user '{USER_ID}'...")
        
        result = collection.delete_many({
            "user_id": USER_ID,
            "message": {"$in": DUMMY_MESSAGES}
        })
        
        print(f"Deleted {result.deleted_count} dummy records.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    cleanup()
