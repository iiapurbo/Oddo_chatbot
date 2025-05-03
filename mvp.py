import streamlit as st
import requests
import uuid

# Set page configuration
st.set_page_config(page_title="Syncoria AI-powered Chatbot", page_icon="🤖")

# Define custom CSS
st.markdown("""
<style>
.assistant-container {
    display: flex;
    margin-bottom: 10px;
}
.user-container {
    display: flex;
    justify-content: flex-end;
    margin-bottom: 10px;
}
.assistant-avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background-color: #2E7D32;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 8px;
    flex-shrink: 0;
}
.assistant-message {
    background-color: #333333;
    padding: 10px 15px;
    border-radius: 15px 15px 15px 0;
    max-width: 70%;
    color: white;
}
.user-message {
    background-color: #1976D2;
    padding: 10px 15px;
    border-radius: 15px 15px 0 15px;
    max-width: 70%;
    color: white;
}
.message-text {
    margin: 0;
}
.chat-title {
    color: white;
    padding: 20px 0;
    text-align: center;
    margin-bottom: 20px;
    font-size: 24px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# Title
st.markdown("<div class='chat-title'>🤖 Syncoria AI-powered Chatbot</div>", unsafe_allow_html=True)

# Initialize session state
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hello! I'm your Business Insights Assistant—what business metric can I fetch for you today?"
        }
    ]

# Function to format message content
def format_message(content):
    if content is None:
        return "No response available"
    if not isinstance(content, str):
        content = str(content)
    return content.replace('\n', '<br>')

# Chat container
chat_container = st.container()
with chat_container:
    for msg in st.session_state.messages:
        if msg["role"] == "assistant":
            st.markdown(f"""
            <div class="assistant-container">
                <div class="assistant-avatar">🤖</div>
                <div class="assistant-message">
                    <p class="message-text">{format_message(msg["content"])}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="user-container">
                <div class="user-message">
                    <p class="message-text">{format_message(msg["content"])}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

# Chat input
user_input = st.chat_input("Type your response...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.rerun()

# Handle assistant response
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.spinner("Analyzing..."):
        payload = {"question": st.session_state.messages[-1]["content"]}
        try:
            response = requests.post(
                "https://9xfvj7u0m8.execute-api.us-east-1.amazonaws.com/dev/chat/generate-response",
                json=payload
            )
            response.raise_for_status()
            response_data = response.json()
            if response_data.get("result") == True and "message" in response_data:
                assistant_response = response_data["message"].get("text_response", "No response available")
            else:
                assistant_response = "Error: Unable to get response"
        except requests.RequestException as e:
            assistant_response = f"Error connecting to the API: {e}"
        
        st.session_state.messages.append({"role": "assistant", "content": assistant_response})
        st.rerun()

# Clear chat history
if st.button("Clear Chat"):
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hello! I'm your Business Insights Assistant—what business metric can I fetch for you today?"
        }
    ]
    st.session_state.session_id = str(uuid.uuid4())
    st.rerun()
