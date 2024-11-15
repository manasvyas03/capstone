import streamlit as st
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv
import os
load_dotenv()

# Configure the API key
genai.configure(api_key=os.environ.get("API"))

# Define the model configuration
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

# System prompt
system_prompt = """
You are an advanced AI medical assistant capable of both analyzing medical reports and providing general health advice. Your task involves two roles:
Role 1: Medical Report Analyzer
When the user provides a medical report or image, you must:

Explain the medical test: Provide a clear explanation of the purpose of the test, including what it measures and why it is typically performed.

Interpret the results: Based on the values or findings in the report, give a detailed explanation of what the results might indicate.

Identify potential health concerns: Offer possible interpretations of abnormal results, mentioning any related conditions or issues the patient might be at risk for, based on the data.

Provide a disclaimer: Clearly state, "I am an AI chatbot providing general information. For a proper diagnosis and treatment plan, please consult a healthcare professional or doctor."

Verify the document: If the document or image provided is not related to the medical field, respond with: "This is not a medical report. Please provide a valid medical report."

Your responses should be accurate, informative, and user-friendly, ensuring the patient understands the information but knows to seek professional advice.

Role 2: General Doctor Chatbot
When the user seeks general health advice or has physical health concerns, you must:

Create a welcoming environment: Greet the user warmly and ask them to describe their physical health issue or symptoms. Be empathetic and ensure they feel comfortable sharing their health concerns.

Assess the symptoms: Ask follow-up questions to understand the user's symptoms, such as the duration, severity, and any other related signs (e.g., fever, fatigue, headache). Encourage them to describe their health problem in detail.

Provide general medical advice: Based on the user’s symptoms, offer general health advice, such as recommending rest, hydration, or over-the-counter remedies. Provide guidance on managing common conditions like colds, flu, stomach ache, or fever. Offer prevention tips when appropriate (e.g., hygiene practices, staying hydrated).

Advise when to seek professional care: If the symptoms are severe, persistent, or beyond what can be managed with basic care, advise the user to consult a healthcare professional. Mention red flags (e.g., high fever for more than 3 days, difficulty breathing) that warrant immediate medical attention.

Offer self-care tips: Provide personalized suggestions for maintaining health and wellness, such as healthy eating, exercise, and sleeping habits, tailored to the user’s condition or general health query.

Provide a disclaimer: Include a statement such as: "I am an AI chatbot here to provide general health advice, but I am not a licensed doctor. For a proper diagnosis and treatment, please consult a healthcare professional."

Emergency intervention: If the user describes a serious condition or symptoms like chest pain or difficulty breathing, respond with: "This sounds like a serious condition. Please seek immediate medical attention or contact emergency services."

Your responses should be informative, supportive, and practical, while also emphasizing the need for professional healthcare assistance when necessary.


"""


# Set page configuration
st.set_page_config(page_title="Medical Assistant", page_icon="robot")

# Apply custom CSS
st.markdown(
    """
    <style>
    /* Change the overall background color */
    .stApp {
        background-color: #96dcff;
    }
    
    /* Change the font color for various elements */
    h1, h2, h3, h4, h5, h6, p, label, .css-10trblm, .css-16huue1, .stMarkdown, .stButton>button, .stTextInput>div>div>input, .stFileUploader>div>label>div {
        color: #005f8a !important;
    }

    /* Change the background of input boxes and button */
    .stTextInput>div>div>input {
        background-color: #96dcff;
        color: #005f8a;
    }

    /* File uploader styling */
    .stFileUploader>div>label>div {
        color: #005f8a;
    }

    /* Button styling */
    .stButton>button {
        background-color: #fff;
        color: #ffffff;
    }

    /* Chat history box */
    .css-1cpxqw2 {
        color: #005f8a;
        background-color: #96dcff;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# Display header image and title
st.image("image.png", width=100)
st.title("Medical Assistant")
st.subheader("Upload a medical report and/or chat with your doctor.")

# Initialize session state to store chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# File uploader for medical report image
uploaded_file = st.file_uploader("Upload a medical report image (optional)", type=["png", "jpg", "jpeg"])

# Display uploaded image if available
if uploaded_file:
    st.image(uploaded_file, width=300)

# Input for user to ask health-related questions
user_input = st.text_input("Ask your question:")

# Button to either chat or analyze the report
submit_button = st.button("Submit")

# When user clicks the 'Submit' button
if submit_button:
    chat_history = st.session_state.chat_history  # Load chat history from session state

    if uploaded_file:
        # If a report is uploaded, first perform report analysis
        image_data = uploaded_file.getvalue()

        # Prepare the image and prompt parts for the model
        image_parts = [
            {
                "mime_type": "image/jpeg",
                "data": image_data
            },
        ]

        prompt_parts = [
            image_parts[0],
            system_prompt
        ]

        # Generate the analysis response
        response = model.generate_content(prompt_parts)

        # Display the analysis result
        if response:
            st.title("Analysis of Report:")
            st.write(response.text)
            chat_history.append({"user": "Uploaded medical report for analysis", "bot": response.text})

    # If the user has entered a question or would like to chat
    if user_input:
        # Combine user input with the system prompt
        if uploaded_file:
            chat_prompt = f"{system_prompt}\nUser uploaded a report and asked: {user_input}\nDoctor:"
        else:
            chat_prompt = f"{system_prompt}\nUser: {user_input}\nDoctor:"

        # Generate the doctor's response
        chat_response = model.generate_content(chat_prompt)

        # Store the question and response in chat history
        if chat_response:
            st.title("Doctor's Response:")
            st.write(chat_response.text)
            chat_history.append({"user": user_input, "bot": chat_response.text})

    # Display the full conversation history
    st.session_state.chat_history = chat_history
    st.subheader("Chat History")
    for chat in chat_history:
        st.write(f"**You:** {chat['user']}")
        st.write(f"**Doctor:** {chat['bot']}")
