import random
import re
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import os
import numpy as np
from datetime import datetime

# Import database connection logic
# Handle potential import errors for local vs deployed environments
try:
    from backend.database import chats_collection as chat_collection, chat_helper, delete_chat
except ImportError:
    try:
        from database import chats_collection as chat_collection, chat_helper, delete_chat
    except ImportError:
         print("Warning: Database module not found or configured.")
         chat_collection = None

app = FastAPI()

# CORS
# Allow all origins for simplicity in this project deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for lazy loading
model = None
vectorizer = None

def get_model_path(filename):
    # Strategy 1: Relative to this file (backend/main.py)
    base_dir_1 = os.path.dirname(os.path.abspath(__file__))
    path_1 = os.path.join(base_dir_1, "models", filename)
    if os.path.exists(path_1):
        return path_1
    
    # Strategy 2: Relative to Current Working Directory (Project Root)
    # Vercel entry point is usually at root, so CWD might be root.
    cwd = os.getcwd()
    path_2 = os.path.join(cwd, "backend", "models", filename)
    if os.path.exists(path_2):
        return path_2
        
    print(f"Warning: Model file {filename} not found at {path_1} or {path_2}")
    print(f"CWD: {cwd}")
    try:
        print(f"Directory listing of {base_dir_1}: {os.listdir(base_dir_1)}")
        print(f"Directory listing of {os.path.join(base_dir_1, 'models')}: {os.listdir(os.path.join(base_dir_1, 'models'))}")
    except:
        pass
    return path_1 # Return default to let calling function fail with path log

def get_model():
    global model, vectorizer
    if model is None or vectorizer is None:
        try:
            model_path = get_model_path("anxiety_model.pkl")
            vectorizer_path = get_model_path("tfidf_vectorizer.pkl")
            
            print(f"Loading model from: {model_path}")
            print(f"Loading vectorizer from: {vectorizer_path}")
            
            model = joblib.load(model_path)
            vectorizer = joblib.load(vectorizer_path)
            print("Model and Vectorizer loaded successfully.")
        except Exception as e:
            print(f"Error loading model: {e}")
            raise HTTPException(status_code=500, detail=f"Model loading failed: {str(e)}")
    return model, vectorizer



# Data Models
class UserInput(BaseModel):
    text: str
    user_id: str = "guest"

class ChatResponse(BaseModel):
    anxiety_level: str
    explanation: str
    suggestions: list[str]

# --- Logic for Suggestions (kept as is) ---
suggestions_db = {
    # ... (Same suggestions logic as before) ...
    "Low Anxiety": [
        ["Great to hear you are feeling okay!", "Maintain your routine.", "Keep practicing mindfulness."],
        ["It's wonderful that you're in a good place.", "Take a moment to appreciate this feeling.", "Engage in a hobby."]
    ],
    "Moderate Anxiety": [
        ["Try deep breathing (4-7-8 technique).", "Take a short walk.", "Listen to calming music."],
        ["Acknowledge your feelings.", "Step away from screens.", "Drink water slowly."]
    ],
    "High Anxiety": [
        ["Consider reaching out to a professional.", "Connect with a friend.", "Practice grounding."],
        ["If unsafe, contact emergency services.", "Focus on breathing.", "Find a quiet space."]
    ]
}

# Empathy Map
empathy_map = {
    "Low Anxiety": ["It sounds like you are in a good headspace.", "I'm glad to see you're feeling balanced."],
    "Moderate Anxiety": ["It is completely normal to feel this way sometimes.", "You might be feeling overwhelmed."],
    "High Anxiety": ["Please remember this feeling is temporary.", "It sounds like you're going through a tough time."]
}

def get_suggestions(level, text=""):
    # Simplified for brevity in this rewrite, assuming logic exists or can be expanded
    # Re-using the logic from previous file if possible, or keeping it simple
    options = suggestions_db.get(level, [])
    if options:
        return random.choice(options)
    return []

def clean_text(text):
    import re
    text = re.sub(r'[^a-zA-Z\s]', '', text).lower().strip()
    return text

def check_harmful_content(text):
    harmful_patterns = [r"suicide", r"kill\s+myself", r"die", r"hurt\s+myself"]
    for p in harmful_patterns:
        if re.search(p, text.lower()):
            return True
    return False

# --- Endpoints ---

@app.get("/")
async def root():
    return {"message": "Social Anxiety Detection API is running"}

@app.post("/predict", response_model=ChatResponse)
async def predict_anxiety(input_data: UserInput = Body(...)):
    if check_harmful_content(input_data.text):
        return {
            "anxiety_level": "High Anxiety",
            "explanation": "Please prioritize your safety. Reach out to a professional.",
            "suggestions": ["Call emergency services", "Contact a trusted friend"]
        }

    # Lazy load model
    model, vectorizer = get_model()

    if not model or not vectorizer:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    clean_input = clean_text(input_data.text)
    if not clean_input:
         raise HTTPException(status_code=400, detail="Input text is empty")

    vectorized_text = vectorizer.transform([clean_input])
    prediction = model.predict(vectorized_text)[0]
    anxiety_level = prediction
    
    suggestions = get_suggestions(anxiety_level)
    
    phrases = empathy_map.get(anxiety_level, [""])
    phrase = random.choice(phrases) if phrases else ""
    explanation = f"Based on your input, the model predicts {anxiety_level}. {phrase}"

    # Autosave to MongoDB if connected
    if chat_collection:
        try:
             chat_entry = {
                "user_id": input_data.user_id,
                "message": input_data.text,
                "response": explanation,
                "anxiety_level": anxiety_level,
                "suggestions": suggestions,
                "timestamp": datetime.utcnow()
            }
             chat_collection.insert_one(chat_entry)
        except Exception as e:
            print(f"Error saving chat: {e}")

    return {
        "anxiety_level": anxiety_level,
        "explanation": explanation,
        "suggestions": suggestions
    }

# Keep other endpoints if needed for history/insights, but sticking to core requirements first.
