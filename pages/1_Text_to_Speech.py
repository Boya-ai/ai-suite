import streamlit as st
import openai
import os
import base64
from tempfile import NamedTemporaryFile
import time

# Import your existing functions from app.py
from app import (
    get_binary_file_downloader_html,
    openai_tts,
    openai_chat_tts,
    load_mms_model,
    mms_tts
)

st.set_page_config(
    page_title="Text to Speech",
    page_icon="🔊",
    layout="wide"
)

# Set OpenAI API key
if 'OPENAI_API_KEY' not in st.secrets:
    st.error("OpenAI API key not found in secrets!")
    st.stop()
else:
    openai.api_key = st.secrets['OPENAI_API_KEY']

st.title("Text to Speech Comparison")

# Create tabs for different functionalities
tab1, tab2, tab3 = st.tabs(["Basic TTS", "Chat TTS", "MMS-TTS"])

with tab1:
    st.header("Basic TTS")
    voice_options = {
        "Nova (Female)": "nova",
        "Alloy (Neutral)": "alloy",
        "Echo (Male)": "echo",
        "Fable (Male)": "fable",
        "Onyx (Male)": "onyx",
        "Shimmer (Female)": "shimmer"
    }
    selected_voice = st.selectbox("Select voice:", list(voice_options.keys()), key="basic_voice")
    text_input = st.text_area("Enter text:", value="שלום עולם", height=150, key="basic_text")
    
    if st.button("Generate Basic TTS"):
        if text_input.strip():
            with st.spinner("Generating audio..."):
                audio_file = openai_tts(text_input, voice=voice_options[selected_voice])
                if audio_file:
                    st.audio(audio_file, format='audio/mp3')
                    st.markdown(get_binary_file_downloader_html(audio_file, "tts_output.mp3"), unsafe_allow_html=True)
                    os.unlink(audio_file)

with tab2:
    st.header("Chat TTS")
    preset_prompts = {
        "British Teacher": "You are a helpful assistant that speaks in a British accent and enunciates like you're talking to a child.",
        "Fast Speaker": "You are a helpful assistant that speaks in a British accent and speaks really fast.",
        "Hebrew Speaker": "You are a helpful female cheerful assistant that speaks in a correct Hebrew accent and enunciates like you're talking to a child.",
        "Custom": "Custom prompt..."
    }
    selected_prompt = st.selectbox("Select speaking style:", list(preset_prompts.keys()), key="chat_prompt")
    
    if selected_prompt == "Custom":
        system_prompt = st.text_area("Enter custom system prompt:", height=100)
    else:
        system_prompt = preset_prompts[selected_prompt]
    
    text_input = st.text_area("Enter text:", value="שלום עולם", height=150, key="chat_text")
    
    if st.button("Generate Chat TTS"):
        if text_input.strip():
            with st.spinner("Generating audio..."):
                audio_file = openai_chat_tts(text_input, system_prompt)
                if audio_file:
                    st.audio(audio_file, format='audio/mp3')
                    st.markdown(get_binary_file_downloader_html(audio_file, "chat_tts_output.mp3"), unsafe_allow_html=True)
                    os.unlink(audio_file)

with tab3:
    st.header("MMS-TTS (Hebrew Specialized)")
    text_input = st.text_area("Enter Hebrew text:", value="שלום עולם", height=150, key="mms_text")
    
    if st.button("Generate MMS TTS"):
        if text_input.strip():
            with st.spinner("Loading MMS model..."):
                mms_model, mms_tokenizer = load_mms_model()
                
            if mms_model is not None and mms_tokenizer is not None:
                with st.spinner("Generating audio..."):
                    audio_file = mms_tts(text_input, mms_model, mms_tokenizer)
                    if audio_file:
                        st.audio(audio_file, format='audio/wav')
                        st.markdown(get_binary_file_downloader_html(audio_file, "mms_tts_output.wav"), unsafe_allow_html=True)
                        os.unlink(audio_file) 
