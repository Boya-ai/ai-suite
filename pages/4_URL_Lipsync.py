import streamlit as st
import os
import requests
import json
import base64
from io import BytesIO
from PIL import Image  # Add PIL import for image processing

# Add debug logging at the very start
try:
    print("Starting URL Lipsync page initialization...")
    
    # First, check if we have access to secrets
    if not hasattr(st, 'secrets'):
        raise Exception("Streamlit secrets not available")
    
    if 'GOOEY_API_KEY' not in st.secrets:
        raise Exception("GOOEY_API_KEY not found in secrets")

    # Set page configuration first, before any other st commands
    st.set_page_config(
        page_title="File Upload Lipsync Generator",
        page_icon="🎭",
        layout="wide"
    )

    # Function definitions remain the same
    def resize_image(image_file, max_size=(200, 200)):
        """Resize image to reduce file size while maintaining aspect ratio"""
        image = Image.open(image_file)
        
        # Convert RGBA to RGB if necessary
        if image.mode == 'RGBA':
            image = image.convert('RGB')
        
        # Calculate new size maintaining aspect ratio
        ratio = min(max_size[0] / image.size[0], max_size[1] / image.size[1])
        new_size = (int(image.size[0] * ratio), int(image.size[1] * ratio))
        image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        # Try progressively lower quality until we get a small enough base64 string
        for quality in [50, 30, 20, 10]:  # Start with quality=50, go down if needed
            buffered = BytesIO()
            image.save(buffered, format="JPEG", quality=quality, optimize=True)  # Added optimize=True
            result = buffered.getvalue()
            
            # Check base64 string length
            data_uri = f"data:image/jpeg;base64,{base64.b64encode(result).decode()}"
            if len(data_uri) <= 2000:  # Give some buffer below 2083 limit
                return result
            
        # If we still haven't gotten a small enough image, reduce size further
        max_size = (100, 100)  # Last resort: tiny image
        ratio = min(max_size[0] / image.size[0], max_size[1] / image.size[1])
        new_size = (int(image.size[0] * ratio), int(image.size[1] * ratio))
        image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        buffered = BytesIO()
        image.save(buffered, format="JPEG", quality=10, optimize=True)
        return buffered.getvalue()

    def process_file_lipsync(image_file, text_prompt, voice_name="nova"):
        """Process video with Gooey.ai Lipsync using uploaded file"""
        try:
            # Resize image before processing
            image_bytes = resize_image(image_file)
            
            # Convert the resized image to base64
            base64_image = base64.b64encode(image_bytes).decode()
            
            # Create proper data URI
            data_uri = f"data:image/jpeg;base64,{base64_image}"
            
            # Log file details (for debugging)
            st.write(f"Original file size: {len(image_file.getvalue())} bytes")
            st.write(f"Resized file size: {len(image_bytes)} bytes")
            st.write(f"Base64 string length: {len(data_uri)} characters")
            
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
                "input_face": data_uri,
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
                timeout=300
            )
            
            # Log response details
            st.write(f"Response status code: {response.status_code}")
            if not response.ok:
                st.write(f"Response content: {response.text}")
            
            return response
        except Exception as e:
            st.error(f"Error in lipsync processing: {str(e)}")
            import traceback
            st.error(f"Full error: {traceback.format_exc()}")
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

    # Main app UI
    try:
        st.title("File Upload Lipsync Generator")
        st.write("Generate lip-synced videos from uploaded images")

        # Create two columns for inputs
        col1, col2 = st.columns(2)

        with col1:
            uploaded_file = st.file_uploader(
                "Upload an image", 
                type=['jpg', 'jpeg', 'png'],
                help="Upload an image containing a face"
            )
            
            if uploaded_file:
                st.image(uploaded_file, caption="Preview of uploaded image")

        with col2:
            voice_options = {
                "Nova (Female)": "nova",
                "Alloy (Neutral)": "alloy",
                "Echo (Male)": "echo",
                "Fable (Male)": "fable",
                "Onyx (Male)": "onyx",
                "Shimmer (Female)": "shimmer"
            }
            selected_voice = st.selectbox("Select voice for the speech", list(voice_options.keys()))
            
            text_prompt = st.text_area(
                "Enter the text to be spoken",
                value="Excited about the new innovations that AI will bring to medical research. With gooey.AI workflows, medical students will have quick summaries of all the literature reviews without any LLM hallucinations.",
                height=150,
                help="Enter the text that will be spoken in the video"
            )

        # Process button
        if st.button("Generate Lipsync"):
            st.write("Button clicked!")  # Debug message
            
            if not uploaded_file:
                st.warning("Please upload an image file.")
            elif not text_prompt.strip():
                st.warning("Please enter some text to be spoken.")
            else:
                st.write("Starting processing...")  # Debug message
                
                # Show API key presence (without revealing the key)
                st.write(f"API Key present: {'GOOEY_API_KEY' in st.secrets}")
                
                with st.spinner("Processing... This may take a few minutes."):
                    try:
                        # Verify API key presence
                        if "GOOEY_API_KEY" not in st.secrets:
                            st.error("GOOEY_API_KEY not found in secrets!")
                            st.stop()
                        
                        st.write(f"Uploaded file type: {uploaded_file.type}")  # Debug message
                        st.write(f"Text length: {len(text_prompt)}")  # Debug message
                        st.write(f"Selected voice: {voice_options[selected_voice]}")  # Debug message
                        
                        response = process_file_lipsync(
                            uploaded_file,
                            text_prompt, 
                            voice_options[selected_voice]
                        )
                        
                        st.write("Response received!")  # Debug message
                        
                        if response is None:
                            st.error("No response received from the API")
                        elif response.ok:
                            result = response.json()
                            st.success("Processing complete!")
                            
                            # Display result details
                            with st.expander("View Processing Details", expanded=True):  # Auto-expand for debugging
                                st.json(result)
                            
                            if "output_url" in result:
                                st.subheader("Generated Video")
                                st.video(result["output_url"])
                                
                                video_data = download_video(result["output_url"])
                                if video_data:
                                    st.download_button(
                                        label="Download Generated Video",
                                        data=video_data,
                                        file_name="generated_video.mp4",
                                        mime="video/mp4"
                                    )
                            else:
                                st.error("No output URL in the response")
                                st.json(result)  # Show full response for debugging
                        else:
                            st.error(f"Failed to process the video. Status code: {response.status_code}")
                            st.error(f"Error response: {response.text}")
                    except Exception as e:
                        st.error("An error occurred during processing!")  # More visible error message
                        st.error(f"Error type: {type(e).__name__}")  # Show error type
                        st.error(f"Error message: {str(e)}")  # Show error message
                        import traceback
                        st.error(f"Full error traceback:\n```\n{traceback.format_exc()}\n```")
                        
                        # Additional debug info
                        st.write("Debug Information:")
                        st.write(f"- File uploaded: {uploaded_file is not None}")
                        if uploaded_file:
                            st.write(f"- File name: {uploaded_file.name}")
                            st.write(f"- File type: {uploaded_file.type}")
                            st.write(f"- File size: {uploaded_file.size} bytes")
                        st.write(f"- Text prompt length: {len(text_prompt)}")
                        st.write(f"- Selected voice: {selected_voice}")

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

    except Exception as e:
        st.error(f"Error in UI initialization: {str(e)}")
        import traceback
        st.error(f"Full error: {traceback.format_exc()}")

except Exception as e:
    # If we can't use st commands yet, fall back to print
    print(f"Critical error during initialization: {str(e)}")
    import traceback
    print(f"Full error: {traceback.format_exc()}")
    
    # Try to show error in streamlit if possible
    try:
        st.error("Failed to initialize the page. Please check the logs.")
        st.error(f"Error: {str(e)}")
    except:
        pass 
