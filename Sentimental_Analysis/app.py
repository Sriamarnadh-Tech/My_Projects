import streamlit as st
import pickle
from sentiment_analysis import preprocess_text

# Load model and vectorizer
with open('sentiment_model.pkl', 'rb') as f:
    model = pickle.load(f)
with open('tfidf_vectorizer.pkl', 'rb') as f:
    vectorizer = pickle.load(f)

# Streamlit app
st.title('Sentiment Analysis Demo')
st.write('Test our trained sentiment analysis model')

# Text input
user_input = st.text_area("Enter text to analyze:", "This product is amazing!")

if st.button('Analyze Sentiment'):
    # Preprocess and predict
    processed_text = preprocess_text(user_input)
    features = vectorizer.transform([processed_text])
    prediction = model.predict(features)[0]
    proba = model.predict_proba(features)[0]
    
    # Display results
    sentiment = "Positive" if prediction == 1 else "Negative"
    confidence = proba[1] if prediction == 1 else proba[0]
    
    st.subheader("Results")
    st.write(f"Sentiment: **{sentiment}**")
    st.write(f"Confidence: {confidence:.1%}")
    st.progress(confidence)
    
    # Show raw probabilities
    with st.expander("Detailed probabilities"):
        st.write(f"Negative: {proba[0]:.1%}")
        st.write(f"Positive: {proba[1]:.1%}")
