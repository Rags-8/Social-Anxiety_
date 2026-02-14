import os
import certifi
from pymongo import MongoClient
from datetime import datetime, timedelta
import random

# Configuration
MONGODB_URI = "mongodb+srv://RaghaviSai123:Raghavi123@cluster0.aydji1p.mongodb.net/social_anxiety_db?retryWrites=true&w=majority"
DB_NAME = "social_anxiety_db"
COLLECTION_NAME = "chat_collection"
USER_ID = "guest_streamlit"

def get_dummy_data():
    base_time = datetime.utcnow()
    data = [
        {
            "user_id": USER_ID,
            "message": "I feel a bit nervous about the presentation tomorrow.",
            "response": "It sounds like you are feeling a bit anxious about the upcoming event. This is normal.",
            "anxiety_level": "Low Anxiety",
            "suggestions": ["Prepare your notes", "Practice in front of a mirror", "Get a good night's sleep"],
            "timestamp": base_time - timedelta(days=5)
        },
        {
            "user_id": USER_ID,
            "message": "I panicked when I walked into the crowded room.",
            "response": "That sounds like a very overwhelming experience. Deep breathing can help.",
            "anxiety_level": "High Anxiety",
            "suggestions": ["Find a quiet corner", "Practice box breathing", "Call a friend"],
            "timestamp": base_time - timedelta(days=4)
        },
        {
            "user_id": USER_ID,
            "message": "I'm worried people are judging me when I eat in public.",
            "response": "You might be experiencing the spotlight effect. Most people are focused on themselves.",
            "anxiety_level": "Moderate Anxiety",
            "suggestions": ["Focus on your food", "Listen to a podcast", "Remind yourself it's okay"],
            "timestamp": base_time - timedelta(days=3)
        },
        {
            "user_id": USER_ID,
            "message": "Had a great time with friends today, felt unexpected calm.",
            "response": "That is wonderful to hear! Holding onto these positive moments is important.",
            "anxiety_level": "Low Anxiety",
            "suggestions": ["Journal about this positive experience", "Plan another outing", "Share your joy"],
            "timestamp": base_time - timedelta(days=2)
        },
        {
            "user_id": USER_ID,
            "message": "I don't want to go to the party, I feel sick just thinking about it.",
            "response": "It seems like your anxiety is manifesting physically. Prioritize your comfort.",
            "anxiety_level": "High Anxiety",
            "suggestions": ["Set a time limit for the party", "Have an exit plan", "Consider if you really need to go"],
            "timestamp": base_time - timedelta(days=1)
        },
         {
            "user_id": USER_ID,
            "message": "I spoke up in the meeting today and it went okay.",
            "response": "That is a huge step! You should be proud of yourself.",
            "anxiety_level": "Low Anxiety",
            "suggestions": ["Reward yourself", "Reflect on what went well", "Keep the momentum"],
            "timestamp": base_time - timedelta(hours=12)
        }
    ]
    return data

def main():
    print("Connecting to MongoDB...")
    try:
        client = MongoClient(MONGODB_URI, tlsCAFile=certifi.where())
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        
        # Verify connection
        client.admin.command('ping')
        print("Connected successfully.")
        
        # Insert Data
        dummy_data = get_dummy_data()
        print(f"Inserting {len(dummy_data)} records for user '{USER_ID}'...")
        
        result = collection.insert_many(dummy_data)
        print(f"Success! Inserted IDs: {len(result.inserted_ids)}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
