import streamlit as st
import os
import requests
import json
from tempfile import NamedTemporaryFile

def process_lipsync(video_file, text_prompt, voice_name="nova"):
    """Process video with Gooey.ai Lipsync"""
    try:
        files = [("input_face", video_file)]
        payload = {
            "functions": None,
            "variables": None,
            "text_prompt": text_prompt,
            "tts_provider": "OPEN_AI",
            "openai_voice_name": voice_name,
            "openai_tts_model": "tts_1",
            "uberduck_voice_name": "the-rock",
            "uberduck_speaking_rate": 1,
            "google_voice_name": "en-AU-Neural2-C",
            "google_speaking_rate": 0.8,
            "google_pitch": -5.25,
            "bark_history_prompt": None,
            "elevenlabs_voice_name": "Patrick",
            "elevenlabs_api_key": None,
            "elevenlabs_voice_id": None,
            "elevenlabs_model": "eleven_multilingual_v2",
            "elevenlabs_stability": 0.5,
            "elevenlabs_similarity_boost": 0.75,
            "elevenlabs_style": 0.3,
            "elevenlabs_speaker_boost": True,
            "azure_voice_name": None,
            "ghana_nlp_tts_language": None,
            "face_padding_top": 0,
            "face_padding_bottom": 12,
            "face_padding_left": 0,
            "face_padding_right": 2,
            "sadtalker_settings": None,
            "selected_model": "Wav2Lip",
        }

        response = requests.post(
            "https://api.gooey.ai/v2/LipsyncTTS/form/",
            headers={
                "Authorization": "bearer " + st.secrets["GOOEY_API_KEY"],
            },
            files=files,
            data={"json": json.dumps(payload)},
        )
        return response
    except Exception as e:
        st.error(f"Error in lipsync processing: {str(e)}")
        return None

# Set page configuration
st.set_page_config(
    page_title="Lipsync Generator",
    page_icon="🎬",
    layout="wide"
)

# Main app
st.title("Lipsync Generator")
st.write("Generate lip-synced videos with custom text and voice")

# Create two columns for inputs
col1, col2 = st.columns(2)

with col1:
    # File uploader
    video_file = st.file_uploader(
        "Upload your video file", 
        type=['mp4', 'mov'],
        help="Upload a video file containing a face"
    )
    
    # Preview uploaded video
    if video_file:
        st.video(video_file)

with col2:
    # Voice selection
    voice_options = {
        "Nova (Female)": "nova",
        "Alloy (Neutral)": "alloy",
        "Echo (Male)": "echo",
        "Fable (Male)": "fable",
        "Onyx (Male)": "onyx",
        "Shimmer (Female)": "shimmer"
    }
    selected_voice = st.selectbox("Select voice for the speech", list(voice_options.keys()))
    
    # Text input
    text_prompt = st.text_area(
        "Enter the text to be spoken",
        height=150,
        help="Enter the text that will be spoken in the video"
    )

# Process button
if st.button("Generate Lipsync"):
    if video_file is None:
        st.warning("Please upload a video file first.")
    elif not text_prompt.strip():
        st.warning("Please enter some text to be spoken.")
    else:
        with st.spinner("Processing... This may take a few minutes."):
            response = process_lipsync(
                video_file, 
                text_prompt, 
                voice_options[selected_voice]
            )
            
            if response and response.ok:
                result = response.json()
                st.success("Processing complete!")
                
                # Display result details
                with st.expander("View Processing Details"):
                    st.json(result)
                
                # If the response includes a video URL, display it
                if "output_url" in result:
                    st.subheader("Generated Video")
                    st.video(result["output_url"])
                    
                    # Add download button for the video
                    st.markdown(f"[Download Generated Video]({result['output_url']})")
            else:
                st.error("Failed to process the video. Please try again.")
                if response:
                    st.error(f"Error: {response.content}")

# Instructions
with st.expander("Instructions and Tips"):
    st.markdown("""
    ### Instructions:
    1. Upload a video file containing a clear face view
    2. Select the desired voice for the speech
    3. Enter the text you want the person to speak
    4. Click 'Generate Lipsync' and wait for processing
    5. Download or preview the generated video

    ### Tips:
    - Use videos with good lighting and clear face visibility
    - Keep the face relatively still and centered
    - Ensure the text length matches the video duration
    - For best results, use high-quality video input
    
    ### Supported Formats:
    - Video: MP4, MOV
    - Maximum file size: 100MB
    - Recommended resolution: 720p or higher
    """) 