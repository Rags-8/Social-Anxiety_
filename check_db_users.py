import certifi
from pymongo import MongoClient
import os

MONGODB_URI = "mongodb+srv://RaghaviSai123:Raghavi123@cluster0.aydji1p.mongodb.net/social_anxiety_db?retryWrites=true&w=majority"
DB_NAME = "social_anxiety_db"
COLLECTION_NAME = "chat_collection"

def check_users():
    try:
        # Use exact working connection style from populate_dummy_data.py
        client = MongoClient(MONGODB_URI, tlsCAFile=certifi.where())
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        
        # Verify connection
        client.admin.command('ping')
        print("Connected successfully.")
        
        # Get distinct user_ids
        user_ids = collection.distinct("user_id")
        print("Found User IDs:", user_ids)
        
        # Count for each
        for uid in user_ids:
            count = collection.count_documents({"user_id": uid})
            print(f"User: {uid} | Count: {count}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_users()
