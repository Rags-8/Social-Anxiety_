import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
import joblib
import os

# Create dummy data
data = {
    'text': [
        "I feel so anxious and nervous all the time.",
        "I'm scared to talk to people.",
        "My heart races when I'm in a crowd.",
        "I prefer to stay home and avoid social situations.",
        "I feel happy and confident today!",
        "Life is good, I enjoy meeting new people.",
        "I am looking forward to the party.",
        "I'm feeling calm and relaxed.",
        "Sometimes I feel a bit stressed but it's manageable.",
        "I have a presentation but I think I can handle it.",
        "I don't like public speaking much.",
        "I feel okay, just a normal day."
    ],
    'label': [
        "High Anxiety", "High Anxiety", "High Anxiety", "High Anxiety",
        "Low Anxiety", "Low Anxiety", "Low Anxiety", "Low Anxiety",
        "Moderate Anxiety", "Moderate Anxiety", "Moderate Anxiety", "Low Anxiety"
    ]
}

df = pd.DataFrame(data)

# Split data (though tiny)
X = df['text']
y = df['label']

# Create pipeline
vectorizer = TfidfVectorizer()
X_vect = vectorizer.fit_transform(X)

model = MultinomialNB()
model.fit(X_vect, y)

# Save models
output_dir = os.path.join("backend", "models")
os.makedirs(output_dir, exist_ok=True)

model_path = os.path.join(output_dir, "anxiety_model.pkl")
vectorizer_path = os.path.join(output_dir, "tfidf_vectorizer.pkl")

joblib.dump(model, model_path)
joblib.dump(vectorizer, vectorizer_path)

print(f"Dummy model saved to {model_path}")
print(f"Dummy vectorizer saved to {vectorizer_path}")
