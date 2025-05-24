import streamlit as st
import numpy as np
import tensorflow as tf
from sklearn.preprocessing import StandardScaler
import joblib

# Title
st.title("🌸 Iris Flower Classifier")
st.write("Predict the type of Iris flower using a pre-trained model (`iris.h5`)")

# Load model
model = tf.keras.models.load_model("Iris.h5")

# Optional: Load scaler if you used one (you must have saved it)
# scaler = joblib.load("scaler.pkl")

# Input sliders
sepal_length = st.slider("Sepal Length (cm)", 4.0, 8.0, 5.8)
sepal_width = st.slider("Sepal Width (cm)", 2.0, 4.5, 3.0)
petal_length = st.slider("Petal Length (cm)", 1.0, 7.0, 4.3)
petal_width = st.slider("Petal Width (cm)", 0.1, 2.5, 1.3)

# Predict button
if st.button("Classify Flower"):
    input_data = np.array([[sepal_length, sepal_width, petal_length, petal_width]])
    
    # Optional: scale the input if your model was trained on scaled data
    # input_data = scaler.transform(input_data)

    prediction = model.predict(input_data)
    predicted_class = np.argmax(prediction)

    class_names = ["Setosa", "Versicolor", "Virginica"]
    st.success(f"🌼 Predicted Iris Flower: **{class_names[predicted_class]}**")
