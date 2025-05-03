import streamlit as st
import requests
import uuid
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# Set page configuration first
st.set_page_config(page_title="Syncoria AI-powered Chatbot", page_icon="🤖")

# Title
st.title("🤖 Syncoria AI-powered Chatbot")

# Define welcome message once
WELCOME_MESSAGE = "Hello! I'm your Business Insights Assistant—what business metric can I fetch for you today?"

# Initialize session state
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": WELCOME_MESSAGE
        }
    ]
if "results" not in st.session_state:
    st.session_state.results = []
if "report" not in st.session_state:
    st.session_state.report = None

# Function to format message content (handle newlines)
def format_message(content):
    # Check if content is None or not a string
    if content is None:
        return "No response available"
        
    # Make sure content is a string
    if not isinstance(content, str):
        content = str(content)
        
    # Replace newlines with HTML line breaks for proper rendering in markdown
    return content.replace('\n', '\n\n')

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🤖" if msg["role"] == "assistant" else None):
        # Use unsafe_allow_html to render the HTML line breaks
        if msg["role"] == "assistant" and "<br>" in msg["content"]:
            st.markdown(msg["content"], unsafe_allow_html=True)
        else:
            st.markdown(msg["content"])

# Chat input at the bottom
user_input = st.chat_input("Type your response...")

if user_input:
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Display the user message immediately
    with st.chat_message("user"):
        st.markdown(user_input)

    # Make API call to the external API endpoint
    try:
        # Add a spinner while generating the response
        with st.spinner("The answer is being generated..."):
            # Use the correct request format based on the Postman collection
            payload = {
                "question": user_input
                # "session_id": st.session_state.session_id  # Uncomment if the API supports it
            }

            response = requests.post(
                "https://9xfvj7u0m8.execute-api.us-east-1.amazonaws.com/dev/chat/generate-response",
                json=payload
            )
            response.raise_for_status()
            response_data = response.json()
            
            # Extract the assistant's response from the correct path in the response
            assistant_response = "No response text available"
            if response_data.get("result") == True and "message" in response_data:
                message_data = response_data["message"]
                if "text_response" in message_data and message_data["text_response"] is not None:
                    assistant_response = message_data["text_response"]
                
            # Format the response to handle newlines properly
            formatted_response = format_message(assistant_response)

            # Add assistant response to history
            st.session_state.messages.append({"role": "assistant", "content": formatted_response})
            
            # Display the assistant's message
            with st.chat_message("assistant", avatar="🤖"):
                if "<br>" in formatted_response:
                    st.markdown(formatted_response, unsafe_allow_html=True)
                else:
                    st.markdown(formatted_response)

    except requests.RequestException as e:
        st.error(f"Error connecting to the API: {e}")
        # Don't add error message to chat history

# Clear chat history
if st.button("Clear Chat"):
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": WELCOME_MESSAGE
        }
    ]
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.results = []
    st.session_state.report = None
    st.rerun()
