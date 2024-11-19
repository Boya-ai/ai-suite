import streamlit as st
import os
import requests
import json
import base64
from io import BytesIO


def process_file_lipsync(image_file, text_prompt, voice_name="nova"):
    """Process video with Gooey.ai Lipsync using uploaded file"""
    try:
        # Get MIME type from the uploaded file
        mime_type = image_file.type
        if not mime_type:
            # Fallback MIME type based on file extension
            if image_file.name.lower().endswith(('.png')):
                mime_type = 'image/png'
            else:
                mime_type = 'image/jpeg'
        
        # Convert the uploaded file to base64
        bytes_data = image_file.getvalue()
        base64_image = base64.b64encode(bytes_data).decode()
        
        # Create proper data URI
        data_uri = f"data:{mime_type};base64,{base64_image}"
        
        # Log file details (for debugging)
        st.write(f"File type: {mime_type}")
        st.write(f"File size: {len(bytes_data)} bytes")
        
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
            "input_face": data_uri,  # Using proper data URI format
            "face_padding_top": 0,
            "face_padding_bottom": 5,
            "face_padding_left": 0,
            "face_padding_right": 0,
            "sadtalker_settings": None,
            "selected_model": "Wav2Lip",
        }

        # Log the API request (without sensitive data)
        st.write("Sending request to Gooey.ai API...")
        
        response = requests.post(
            "https://api.gooey.ai/v2/LipsyncTTS",
            headers={
                "Authorization": f"bearer {st.secrets['GOOEY_API_KEY']}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=300  # Added timeout of 5 minutes
        )
        
        # Log response details
        st.write(f"Response status code: {response.status_code}")
        if not response.ok:
            st.write(f"Response content: {response.text}")
            
        return response
    except requests.exceptions.Timeout:
        st.error("Request timed out. The server took too long to respond.")
        return None
    except Exception as e:
        st.error(f"Error in lipsync processing: {str(e)}")
        import traceback
        st.error(f"Full error: {traceback.format_exc()}")
        return None
