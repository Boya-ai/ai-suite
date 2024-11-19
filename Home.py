import streamlit as st

st.set_page_config(
    page_title="AI Voice Tools",
    page_icon="🎙️",
    layout="wide"
)

st.title("AI Voice Tools Hub")
st.markdown("""
Welcome to the AI Voice Tools Hub! This application provides various AI-powered voice and speech tools:

### 🗣️ Available Tools:

1. **Text to Speech Comparison**
   - Compare different TTS models
   - Support for Hebrew text
   - Multiple voices and styles
   - Download capabilities

2. **Voice Chat Assistant**
   - Interactive chat with voice responses
   - Multiple speaking styles
   - Chat history tracking
   - Download conversation audio

3. **Lipsync Generator**
   - Generate lip-synced videos
   - Multiple voice options
   - Custom text prompts
   - Professional video output

### 🚀 Getting Started:
- Select a tool from the sidebar
- Follow the instructions for each tool
- Experiment with different settings

### 📝 Notes:
- All tools support Hebrew text
- Audio files can be downloaded
- Settings can be customized
""")

# Add footer
st.markdown("""
---
Made with ❤️ using OpenAI, Streamlit, and Gooey.ai
""") 