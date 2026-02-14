import random
import re
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import os
from datetime import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId

# --- MongoDB Configuration ---
import certifi

MONGODB_URI = os.getenv(
    "MONGODB_URI",
    "mongodb+srv://RaghaviSai123:Raghavi123@cluster0.aydji1p.mongodb.net/social_anxiety_db?appName=Cluster0"
)
DB_NAME = "social_anxiety_db"
COLLECTION_NAME = "chat_collection"

# Connect to MongoDB with SSL Context
try:
    print(f"[INFO] Attempting to connect to MongoDB...")
    client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000, tlsCAFile=certifi.where())
    db = client[DB_NAME]
    chat_collection = db[COLLECTION_NAME]
    # Trigger a real connection check
    client.admin.command('ping')
    print(f"[SUCCESS] Connected to MongoDB: {DB_NAME}.{COLLECTION_NAME}")
except Exception as e:
    print(f"[ERROR] MongoDB connection failed: {e}")
    chat_collection = None

# --- Database Helper ---
def chat_helper(chat) -> dict:
    return {
        "id": str(chat["_id"]),
        "user_id": chat.get("user_id"),
        "message": chat.get("message"),
        "response": chat.get("response"),
        "anxiety_level": chat.get("anxiety_level"),
        "suggestions": chat.get("suggestions"),
        "timestamp": str(chat.get("timestamp"))
    }

# --- FastAPI Setup ---
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ML Model Lazy Loading ---
model = None
vectorizer = None

def get_model_path(filename):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    path1 = os.path.join(base_dir, "models", filename)
    path2 = os.path.join(os.getcwd(), "backend", "models", filename)
    if os.path.exists(path1): return path1
    if os.path.exists(path2): return path2
    print(f"❌ Model {filename} not found!")
    return path1

def get_model():
    global model, vectorizer
    if model is None or vectorizer is None:
        try:
            model = joblib.load(get_model_path("anxiety_model.pkl"))
            vectorizer = joblib.load(get_model_path("tfidf_vectorizer.pkl"))
            print("✅ Models loaded successfully.")
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            raise HTTPException(status_code=500, detail=f"Model loading failed: {e}")
    return model, vectorizer

# --- Anxiety Logic ---
suggestions_db = {
    "Low Anxiety": [["Great to hear you are feeling okay!", "Maintain your routine.", "Keep practicing mindfulness."]],
    "Moderate Anxiety": [["Try deep breathing.", "Take a short walk.", "Listen to calming music."]],
    "High Anxiety": [["Consider reaching out to a professional.", "Connect with a friend.", "Practice grounding."]]
}

empathy_map = {
    "Low Anxiety": ["It sounds like you are in a good headspace.", "I'm glad to see you're feeling balanced."],
    "Moderate Anxiety": ["It is completely normal to feel this way sometimes.", "You might be feeling overwhelmed."],
    "High Anxiety": ["Please remember this feeling is temporary.", "It sounds like you're going through a tough time."]
}

def get_suggestions(level):
    options = suggestions_db.get(level, [])
    return random.choice(options) if options else []

def clean_text(text):
    return re.sub(r'[^a-zA-Z\s]', '', text).lower().strip()

def check_harmful_content(text):
    harmful_patterns = [r"suicide", r"kill\s+myself", r"die", r"hurt\s+myself"]
    return any(re.search(p, text.lower()) for p in harmful_patterns)

# --- API Models ---
class UserInput(BaseModel):
    text: str
    user_id: str = "guest"

class ChatResponse(BaseModel):
    anxiety_level: str
    explanation: str
    suggestions: list[str]

# --- Endpoints ---
@app.get("/")
async def root():
    return {"message": "Social Anxiety Detection API is running (DB Connected)"}

@app.post("/predict", response_model=ChatResponse)
async def predict_anxiety(input_data: UserInput = Body(...)):
    # Safety Check
    if check_harmful_content(input_data.text):
        return {
            "anxiety_level": "High Anxiety",
            "explanation": "Please prioritize your safety. Reach out to a professional.",
            "suggestions": ["Call emergency services", "Contact a trusted friend"]
        }

    # Load Model
    model, vectorizer = get_model()
    clean_input = clean_text(input_data.text)
    if not clean_input:
        raise HTTPException(status_code=400, detail="Input text is empty")

    # Prediction
    vectorized = vectorizer.transform([clean_input])
    prediction = model.predict(vectorized)[0]
    suggestions = get_suggestions(prediction)
    phrase = random.choice(empathy_map.get(prediction, [""]))
    explanation = f"Based on your input, the model predicts {prediction}. {phrase}"

    # Save to MongoDB
    if chat_collection is not None:
        try:
            chat_entry = {
                "user_id": input_data.user_id,
                "message": input_data.text,
                "response": explanation,
                "anxiety_level": prediction,
                "suggestions": suggestions,
                "timestamp": datetime.utcnow()
            }
            result = chat_collection.insert_one(chat_entry)
            print(f"[SUCCESS] Saved chat: {result.inserted_id}")
        except Exception as e:
            print(f"[ERROR] Failed to save chat: {e}")

    return {"anxiety_level": prediction, "explanation": explanation, "suggestions": suggestions}

@app.get("/history/{user_id}")
async def get_history(user_id: str):
    if chat_collection is None:
        return []
    try:
        # Fetch all chats for the user, sorted by newest first
        # Note: If user_id is 'guest_streamlit' or similar, we might want to filter.
        # Ideally filter by user_id: {"user_id": user_id}
        # But if the app uses a shared DB for demo, maybe return all?
        # The Streamlit app sends a specific USER_ID. Let's filter by it.
        # If user_id is "all", we return all.
        
        filter_query = {} if user_id == "all" else {"user_id": user_id}
        
        # Fallback: if user_id is strictly required by logic but Streamlit sends generic "guest_streamlit",
        # ensure we catch data even if saved under different IDs if desired? 
        # No, strict filtering is better for a real app.
        
        chats = list(chat_collection.find(filter_query).sort("timestamp", -1))
        return [chat_helper(chat) for chat in chats]
    except Exception as e:
        print(f"Error fetching history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/delete_chat/{chat_id}")
async def delete_chat_endpoint(chat_id: str):
    if chat_collection is None:
        raise HTTPException(status_code=503, detail="Database not connected")
    try:
        result = chat_collection.delete_one({"_id": ObjectId(chat_id)})
        if result.deleted_count > 0:
            return {"message": "Chat deleted"}
        raise HTTPException(status_code=404, detail="Chat not found")
    except Exception as e:
        print(f"Error deleting chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_insights/{user_id}")
async def get_insights(user_id: str):
    if chat_collection is None:
        return {"low": 0, "moderate": 0, "high": 0}
    try:
        # Filter by user_id
        filter_query = {} if user_id == "all" else {"user_id": user_id}
        
        chats = list(chat_collection.find(filter_query))
        low = sum(1 for c in chats if "Low" in c.get("anxiety_level", ""))
        mod = sum(1 for c in chats if "Moderate" in c.get("anxiety_level", ""))
        high = sum(1 for c in chats if "High" in c.get("anxiety_level", ""))
        
        return {"low": low, "moderate": mod, "high": high}
    except Exception as e:
        print(f"Error generating insights: {e}")
        return {"low": 0, "moderate": 0, "high": 0}

    except Exception as e:
        print(f"Error generating insights: {e}")
        return {"low": 0, "moderate": 0, "high": 0}
