import streamlit as st
import openai
import os
import base64
from tempfile import NamedTemporaryFile
import time

def get_binary_file_downloader_html(bin_file, file_label='File'):
    with open(bin_file, 'rb') as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    return f'<a href="data:application/octet-stream;base64,{b64}" download="{file_label}">Download {file_label}</a>'

def openai_tts(text, voice="nova"):
    """Convert text to speech using OpenAI's basic TTS API"""
    try:
        response = openai.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text
        )
        
        with NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            response.stream_to_file(fp.name)
            return fp.name
    except Exception as e:
        st.error(f"Error generating speech with OpenAI TTS: {str(e)}")
        return None

def chat_with_gpt(messages):
    """Chat with GPT and get text response"""
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error in chat completion: {str(e)}")
        return None

# Set page configuration
st.set_page_config(
    page_title="Voice Chat Assistant",
    page_icon="🗣️",
    layout="wide"
)

# Set OpenAI API key
if 'OPENAI_API_KEY' not in st.secrets:
    st.error("OpenAI API key not found in secrets!")
    st.stop()
else:
    openai.api_key = st.secrets['OPENAI_API_KEY']

# Initialize session state for chat history
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Main app
st.title("Voice Chat Assistant")

# Two-column layout for settings
col1, col2 = st.columns(2)

with col1:
    voice_options = {
        "Nova (Female)": "nova",
        "Alloy (Neutral)": "alloy",
        "Echo (Male)": "echo",
        "Fable (Male)": "fable",
        "Onyx (Male)": "onyx",
        "Shimmer (Female)": "shimmer"
    }
    selected_voice = st.selectbox("Select voice:", list(voice_options.keys()))

with col2:
    preset_prompts = {
        "British Teacher": "You are a helpful assistant that speaks in a British accent and enunciates like you're talking to a child.",
        "Fast Speaker": "You are a helpful assistant that speaks in a British accent and speaks really fast.",
        "Hebrew Speaker": "You are a helpful female cheerful assistant that speaks in a correct Hebrew accent and enunciates like you're talking to a child.",
        "Custom": "Custom prompt..."
    }
    selected_prompt = st.selectbox("Select speaking style:", list(preset_prompts.keys()))

if selected_prompt == "Custom":
    system_prompt = st.text_area("Enter custom system prompt:", 
                               height=100,
                               help="Describe how you want the assistant to speak")
else:
    system_prompt = preset_prompts[selected_prompt]

# Initialize or update system message
if not st.session_state.messages:
    st.session_state.messages = [{"role": "system", "content": system_prompt}]
else:
    st.session_state.messages[0] = {"role": "system", "content": system_prompt}

# Chat interface
st.subheader("Chat")
user_input = st.text_area("Your message:", height=100)

if st.button("Send and Speak"):
    if user_input.strip():
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Get GPT response
        response = chat_with_gpt(st.session_state.messages)
        
        if response:
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            # Generate speech for the response
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            audio_file = openai_tts(response, voice=voice_options[selected_voice])
            
            if audio_file:
                # Create columns for response display
                text_col, audio_col = st.columns([3, 1])
                
                with text_col:
                    st.write("Assistant:", response)
                
                with audio_col:
                    st.audio(audio_file, format='audio/mp3')
                    download_filename = f"response_{timestamp}.mp3"
                    st.markdown(get_binary_file_downloader_html(audio_file, download_filename), unsafe_allow_html=True)
                
                # Cleanup
                os.unlink(audio_file)

# Display chat history in a scrollable container
st.subheader("Chat History")
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages[1:]:  # Skip the system message
        role = "You" if message["role"] == "user" else "Assistant"
        st.write(f"{role}: {message['content']}")

# Clear chat history button
if st.button("Clear Chat History"):
    st.session_state.messages = [{"role": "system", "content": system_prompt}]
    st.experimental_rerun()

# Instructions in an expander
with st.expander("Instructions and Notes"):
    st.markdown("""
    ### Instructions:
    1. Select a voice and speaking style for the assistant
    2. Type your message (Hebrew or English)
    3. Click 'Send and Speak' to get both text and voice response
    4. Listen to the response or download it
    5. View the chat history below
    6. Clear chat history if needed

    ### Notes:
    - The assistant will respond based on the selected speaking style
    - You can download any response as an MP3 file
    - The chat history is preserved during your session
    - Different speaking styles will affect how the assistant responds
    """) 