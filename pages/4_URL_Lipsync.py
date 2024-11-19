import streamlit as st
import os
import requests
import json
import base64
from io import BytesIO

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
    def process_file_lipsync(image_file, text_prompt, voice_name="nova"):
        # ... (rest of the function remains the same)
        pass

    def download_video(url):
        # ... (rest of the function remains the same)
        pass

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
            # ... (rest of the button logic remains the same)
            pass

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
