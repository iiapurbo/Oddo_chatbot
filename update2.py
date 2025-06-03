import streamlit as st
import requests
import uuid
import json
import time

# Set page configuration
st.set_page_config(page_title="Syncoria AI-powered Chatbot", page_icon="🤖")

# Define custom CSS with updated .chat-title color
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
    color: var(--text-color);
    padding: 20px 0;
    text-align: center;
    margin-bottom: 20px;
    font-size: 24px;
    font-weight: bold;
}
.typing-indicator {
    display: inline-block;
    margin-left: 5px;
}
.typing-indicator span {
    display: inline-block;
    width: 8px;
    height: 8px;
    background-color: #fff;
    border-radius: 50%;
    margin-right: 3px;
    animation: typing 1s infinite;
}
.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }
@keyframes typing {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-5px); }
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

def format_message(content):
    if content is None:
        return "No response available"
    if not isinstance(content, str):
        content = str(content)
    
    # Convert markdown to HTML
    import re
    
    # Convert **bold** to <strong>bold</strong>
    content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', content)
    
    # Convert ## headers to <h3> (since it's in a chat bubble)
    content = re.sub(r'^## (.*?)$', r'<h3>\1</h3>', content, flags=re.MULTILINE)
    
    # Convert line breaks
    content = content.replace('\n', '<br>')
    
    return content

def stream_response(response_text):
    """Stream the response text word by word with a typing effect."""
    words = response_text.split()
    placeholder = st.empty()
    full_response = ""
    
    # First, show the typing indicator
    placeholder.markdown(f"""
    <div class="assistant-container">
        <div class="assistant-avatar">🤖</div>
        <div class="assistant-message">
            <p class="message-text">Typing<span class="typing-indicator"><span></span><span></span><span></span></span></p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Small delay to show typing indicator
    time.sleep(0.5)
    
    # Now stream the actual response
    for word in words:
        full_response += word + " "
        placeholder.markdown(f"""
        <div class="assistant-container">
            <div class="assistant-avatar">🤖</div>
            <div class="assistant-message">
                <p class="message-text">{full_response}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        time.sleep(0.05)  # Adjust this value to control typing speed
    
    # Return the complete response for proper formatting
    return response_text

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
    with st.spinner(""):
        payload = {"query": st.session_state.messages[-1]["content"]}
        try:
            response = requests.post(
                "https://b2h8gu3v15.execute-api.us-east-1.amazonaws.com/dev/query",
                json=payload
            )
            response.raise_for_status()
            response_data = response.json()
            
            # Extract the descriptive_summary from the API response
            if "analysis" in response_data:
                assistant_response = response_data["analysis"]
                # Stream the response
                streamed_response = stream_response(assistant_response)
                st.session_state.messages.append({"role": "assistant", "content": streamed_response})
            else:
                assistant_response = "Error: Unable to get response"
                st.session_state.messages.append({"role": "assistant", "content": assistant_response})
                
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
