import streamlit as st
import openai
import os
import base64
from tempfile import NamedTemporaryFile
from transformers import VitsModel, AutoTokenizer
import torch
import numpy as np
import scipy.io.wavfile as wav
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

def openai_chat_tts(text, system_prompt):
    """Convert text to speech using OpenAI's Chat Completions TTS"""
    try:
        completion = openai.chat.completions.create(
            model="gpt-4o-audio-preview",
            modalities=["text", "audio"],
            audio={"voice": "alloy", "format": "mp3"},
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": text,
                }
            ],
        )
        
        # Decode and save the audio
        with NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            mp3_bytes = base64.b64decode(completion.choices[0].message.audio.data)
            fp.write(mp3_bytes)
            return fp.name
    except Exception as e:
        st.error(f"Error generating speech with OpenAI Chat TTS: {str(e)}")
        return None

@st.cache_resource
def load_mms_model():
    """Load the MMS-TTS model"""
    try:
        model = VitsModel.from_pretrained("facebook/mms-tts-heb")
        tokenizer = AutoTokenizer.from_pretrained("facebook/mms-tts-heb")
        return model, tokenizer
    except Exception as e:
        st.error(f"Error loading MMS model: {str(e)}")
        return None, None

def mms_tts(text, model, tokenizer):
    """Convert text to speech using MMS-TTS"""
    try:
        # Tokenize the text
        inputs = tokenizer(text=text, return_tensors="pt")
        
        # Generate speech with torch.no_grad()
        with torch.no_grad():
            # The VITS model outputs a dictionary with 'waveform' key
            output = model(**inputs)
            waveform = output.waveform[0]  # Get the first waveform from batch
        
        # Save the audio to a temporary file
        with NamedTemporaryFile(delete=False, suffix=".wav") as fp:
            # Convert to numpy array and scale to int16 range
            audio_np = waveform.numpy()
            audio_np = np.int16(audio_np * 32767)
            wav.write(fp.name, model.config.sampling_rate, audio_np)
            return fp.name
    except Exception as e:
        st.error(f"Error generating speech with MMS-TTS: {str(e)}")
        return None

# Set page configuration
st.set_page_config(
    page_title="Hebrew Text-to-Speech Comparison",
    page_icon="🗣️",
)

# Set OpenAI API key
if 'OPENAI_API_KEY' not in st.secrets:
    st.error("OpenAI API key not found in secrets!")
    st.stop()
else:
    openai.api_key = st.secrets['OPENAI_API_KEY']

# Load MMS model
mms_model, mms_tokenizer = load_mms_model()

# Main app
st.title("Hebrew Text-to-Speech Comparison")
st.write("Compare different TTS models for Hebrew text")

# Model selection
model_choice = st.radio(
    "Choose TTS Model(s)",
    ["OpenAI TTS", "OpenAI Chat TTS", "MMS-TTS", "Compare All"],
    horizontal=True
)

# OpenAI voice selection (only show if OpenAI TTS is selected)
if model_choice in ["OpenAI TTS", "Compare All"]:
    st.subheader("OpenAI TTS Settings")
    voice_options = {
        "Nova (Female)": "nova",
        "Alloy (Neutral)": "alloy",
        "Echo (Male)": "echo",
        "Fable (Male)": "fable",
        "Onyx (Male)": "onyx",
        "Shimmer (Female)": "shimmer"
    }
    selected_voice = st.selectbox("Select OpenAI voice:", list(voice_options.keys()))

# Chat TTS settings (only show if Chat TTS is selected)
if model_choice in ["OpenAI Chat TTS", "Compare All"]:
    st.subheader("OpenAI Chat TTS Settings")
    preset_prompts = {
        "British Teacher": "You are a helpful assistant that speaks in a British accent and enunciates like you're talking to a child.",
        "Fast Speaker": "You are a helpful assistant that speaks in a British accent and speaks really fast.",
        "Hebrew Speaker": "You are a helpful female chearful assistant that speaks in a correct Hebrew accent and enunciates like you're talking to a child.",
        "Custom": "Custom prompt..."
    }
    selected_prompt = st.selectbox("Select speaking style:", list(preset_prompts.keys()))
    
    if selected_prompt == "Custom":
        system_prompt = st.text_area("Enter custom system prompt:", 
                                   height=100,
                                   help="Describe how you want the assistant to speak")
    else:
        system_prompt = preset_prompts[selected_prompt]

# Text input
text_input = st.text_area("Enter Hebrew text:", value="שלום עולם", height=150)

# Generate button
if st.button("Generate Speech"):
    if not text_input.strip():
        st.warning("Please enter some text first.")
        st.stop()

    # Create a timestamp for unique filenames
    timestamp = time.strftime("%Y%m%d-%H%M%S")

    if model_choice in ["OpenAI TTS", "Compare All"]:
        st.subheader("OpenAI TTS Output")
        with st.spinner("Generating OpenAI TTS audio..."):
            openai_audio = openai_tts(text_input, voice=voice_options[selected_voice])
            if openai_audio:
                st.audio(openai_audio, format='audio/mp3')
                # Add download button
                download_filename = f"openai_tts_{timestamp}.mp3"
                st.markdown(get_binary_file_downloader_html(openai_audio, download_filename), unsafe_allow_html=True)
                os.unlink(openai_audio)

    if model_choice in ["OpenAI Chat TTS", "Compare All"]:
        st.subheader("OpenAI Chat TTS Output")
        with st.spinner("Generating OpenAI Chat TTS audio..."):
            chat_audio = openai_chat_tts(text_input, system_prompt)
            if chat_audio:
                st.audio(chat_audio, format='audio/mp3')
                # Add download button
                download_filename = f"openai_chat_tts_{timestamp}.mp3"
                st.markdown(get_binary_file_downloader_html(chat_audio, download_filename), unsafe_allow_html=True)
                os.unlink(chat_audio)

    if model_choice in ["MMS-TTS", "Compare All"]:
        st.subheader("MMS-TTS Output")
        with st.spinner("Generating MMS-TTS audio..."):
            if mms_model is not None and mms_tokenizer is not None:
                mms_audio = mms_tts(text_input, mms_model, mms_tokenizer)
                if mms_audio:
                    st.audio(mms_audio, format='audio/wav')
                    # Add download button
                    download_filename = f"mms_tts_{timestamp}.wav"
                    st.markdown(get_binary_file_downloader_html(mms_audio, download_filename), unsafe_allow_html=True)
                    os.unlink(mms_audio)
            else:
                st.error("MMS-TTS model failed to load")

# Update the instructions to include download information
st.markdown("""
---
### Instructions:
1. Choose the TTS model(s) you want to use
2. If using OpenAI TTS, select a voice from the dropdown menu
3. Type or paste Hebrew text in the text area above
4. Click the 'Generate Speech' button
5. Wait for the audio player(s) to appear
6. Press play to hear the text being read
7. Click the download link below each audio player to save the file

### Notes:
- OpenAI's TTS API may not perfectly pronounce Hebrew text
- MMS-TTS is specifically trained for Hebrew but may sound more robotic
- Compare both to choose the best option for your needs
- Downloaded files will include a timestamp to prevent naming conflicts
""") 