import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import string
import nltk
import pickle

# Download stopwords if needed
nltk.download('stopwords')

# Text preprocessing
def preprocess_text(text):
    # Convert to lowercase
    text = text.lower()
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    words = text.split()
    words = [word for word in words if word not in stop_words]
    # Stemming
    stemmer = PorterStemmer()
    words = [stemmer.stem(word) for word in words]
    return ' '.join(words)

# Load data - handle quoted and space-separated values
df = pd.read_csv('sentiment-analysis.csv', sep=' *, *', engine='python')

# Print column names for debugging
print("Columns in dataset:", df.columns.tolist())

# Clean column names (remove quotes and whitespace)
df.columns = df.columns.str.strip().str.strip('"')

# Clean data - remove rows with missing values
print(f"Initial rows: {len(df)}")
df = df.dropna(subset=['Text', 'Sentiment'])
print(f"Rows after cleaning: {len(df)}")

# Convert sentiment to binary (0/1) if needed
df['Sentiment'] = df['Sentiment'].map({'Positive': 1, 'Negative': 0})

# Preprocess text
df['processed_text'] = df['Text'].apply(preprocess_text)

# Convert text to features
tfidf = TfidfVectorizer(max_features=5000)
X = tfidf.fit_transform(df['processed_text'])
y = df['Sentiment']

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train model
model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# Save model and vectorizer
with open('sentiment_model.pkl', 'wb') as f:
    pickle.dump(model, f)
with open('tfidf_vectorizer.pkl', 'wb') as f:
    pickle.dump(tfidf, f)

print("Model and vectorizer saved successfully")
