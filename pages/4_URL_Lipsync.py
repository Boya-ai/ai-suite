import streamlit as st
import os
import requests
import json
import base64
from io import BytesIO

def process_file_lipsync(image_file, text_prompt, voice_name="nova"):
    """Process video with Gooey.ai Lipsync using uploaded file"""
    try:
        # Convert the uploaded file to base64
        bytes_data = image_file.getvalue()
        base64_image = base64.b64encode(bytes_data).decode()
        
        payload = {
            "functions": None,
            "variables": None,
            "text_prompt": text_prompt,
            "tts_provider": "OPEN_AI",
            "uberduck_voice_name": "the-rock",
            "uberduck_speaking_rate": 1,
            "google_voice_name": "en-AU-Neural2-C",
            "google_speaking_rate": 0.8,
            "google_pitch": -5.25,
            "bark_history_prompt": None,
            "elevenlabs_voice_name": None,
            "elevenlabs_api_key": None,
            "elevenlabs_voice_id": "ODq5zmih8GrVes37Dizd",
            "elevenlabs_model": "eleven_multilingual_v2",
            "elevenlabs_stability": 0.5,
            "elevenlabs_similarity_boost": 0.75,
            "elevenlabs_style": 0.3,
            "elevenlabs_speaker_boost": True,
            "azure_voice_name": None,
            "openai_voice_name": voice_name,
            "openai_tts_model": "tts_1",
            "ghana_nlp_tts_language": None,
            "input_face": f"data:image/jpeg;base64,{base64_image}",  # Send as base64
            "face_padding_top": 0,
            "face_padding_bottom": 5,
            "face_padding_left": 0,
            "face_padding_right": 0,
            "sadtalker_settings": None,
            "selected_model": "Wav2Lip",
        }

        response = requests.post(
            "https://api.gooey.ai/v2/LipsyncTTS",
            headers={
                "Authorization": "bearer " + st.secrets["GOOEY_API_KEY"],
            },
            json=payload,
        )
        return response
    except Exception as e:
        st.error(f"Error in lipsync processing: {str(e)}")
        return None

def download_video(url):
    """Download video from URL and return as bytes"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.content
    except Exception as e:
        st.error(f"Error downloading video: {str(e)}")
        return None

# Set page configuration
st.set_page_config(
    page_title="File Upload Lipsync Generator",
    page_icon="🎭",
    layout="wide"
)

# Main app
st.title("File Upload Lipsync Generator")
st.write("Generate lip-synced videos from uploaded images")

# Create two columns for inputs
col1, col2 = st.columns(2)

with col1:
    # File uploader
    uploaded_file = st.file_uploader(
        "Upload an image", 
        type=['jpg', 'jpeg', 'png'],
        help="Upload an image containing a face"
    )
    
    # Preview image
    if uploaded_file:
        st.image(uploaded_file, caption="Preview of uploaded image")

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
        value="Excited about the new innovations that AI will bring to medical research. With gooey.AI workflows, medical students will have quick summaries of all the literature reviews without any LLM hallucinations.",
        height=150,
        help="Enter the text that will be spoken in the video"
    )

# Process button
if st.button("Generate Lipsync"):
    if not uploaded_file:
        st.warning("Please upload an image file.")
    elif not text_prompt.strip():
        st.warning("Please enter some text to be spoken.")
    else:
        with st.spinner("Processing... This may take a few minutes."):
            response = process_file_lipsync(
                uploaded_file,
                text_prompt, 
                voice_options[selected_voice]
            )
            
            if response and response.ok:
                result = response.json()
                st.success("Processing complete!")
                
                # Display result details
                with st.expander("View Processing Details"):
                    st.json(result)
                
                # If the response includes a video URL, display it and enable download
                if "output_url" in result:
                    st.subheader("Generated Video")
                    st.video(result["output_url"])
                    
                    # Download the video and create a download button
                    video_data = download_video(result["output_url"])
                    if video_data:
                        st.download_button(
                            label="Download Generated Video",
                            data=video_data,
                            file_name="generated_video.mp4",
                            mime="video/mp4"
                        )
            else:
                st.error("Failed to process the video. Please try again.")
                if response:
                    st.error(f"Error: {response.content}")

# Instructions
with st.expander("Instructions and Tips"):
    st.markdown("""
    ### Instructions:
    1. Upload an image containing a clear face view
    2. Select the desired voice for the speech
    3. Enter the text you want the person to speak
    4. Click 'Generate Lipsync' and wait for processing
    5. Download or preview the generated video

    ### Tips:
    - Use images with good lighting and clear face visibility
    - The face should be relatively front-facing
    - For best results, use high-quality images
    
    ### Supported Formats:
    - Supported image formats: JPG, PNG
    - The image should contain a single, clear face
    - The face should be well-lit and centered
    """)
