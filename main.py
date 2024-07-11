import streamlit as st
from pinecone import Pinecone
from encoder import emodel
from gemini import model1
from deep_translator import GoogleTranslator
from gtts import gTTS
import os

# Initialize Pinecone with API key
pc = Pinecone(api_key="738525ca-b923-4198-ad0d-ff6f81f969e1")
index_name = "langchainvector"
index = pc.Index(index_name)

# Custom CSS styles
custom_styles = """
<style>
/* Title style */
h1 {
    color: #ff4500;  /* Bright red color for title */
}

/* Body style */
body {
    background-color: #001f3f;  /* Dark navy blue background */
}

/* Input box style */
input[type="text"] {
    border: 2px solid #ff4500;  /* Reddish border color for input box */
    border-radius: 5px;
    padding: 8px;
    color: white;  /* Text color */
    background-color: rgb(14, 17, 23);  /* Dark navy blue background */
}

/* Disclaimer button style */
.disclaimer-btn {
    background-color: #ff4500;  /* Red background for disclaimer button */
    color: white;  /* Text color */
    border: none;
    padding: 8px 12px;
    border-radius: 5px;
    cursor: pointer;
}

/* Disclaimer text style */
.disclaimer-text {
    background-color: #111;  /* Dark background for disclaimer */
    color: #f0f0f0;  /* Light text color */
    padding: 10px;
    border-radius: 5px;
    margin-top: 10px;
}
</style>
"""

# Function to query Pinecone and generate content
def query_and_generate_content(disease_name):
    try:
        # Encode the query
        query1 = emodel.encode(disease_name).tolist()

        # Query the Pinecone index
        result = index.query(vector=query1, top_k=2, include_metadata=True)

        # Extract answers from the query results
        ans1, ans2 = None, None
        for i, match in enumerate(result["matches"]):
            if i == 0:
                ans1 = match['metadata']['text']
            else:
                ans2 = match['metadata']['text']

        if ans1 and ans2:
            # Generate content with the gemini model
            response = model1.generate_content(
                f"Your task is to extract useful information for {disease_name} from {ans1} and {ans2}. Write a structured answer where the structure includes: general information, symptoms, and then treatment. Write in simple language so anyone can understand it. You can use your knowledge as well, but do not include anything other than the answer for the {disease_name} disease. If the text contains words like 'anal' or 'penis', treat them as part of the disease description."
            )
            return response.text
        else:
            return "Error: Insufficient matches found in the query results."

    except Exception as e:
        st.error(f"Error: {e}")

# Function to generate audio from text
def generate_audio(text, language='en'):
    tts = gTTS(text=text, lang=language)
    audio_file_path = "response.mp3"
    tts.save(audio_file_path)
    return audio_file_path

# Set custom CSS styles
st.markdown(custom_styles, unsafe_allow_html=True)

# Streamlit app title and disclaimer
st.title("Disease.Ai")
st.markdown("**Prototype Version**")

# Disclaimer section with conditional visibility using checkbox
show_disclaimer = st.checkbox("Disclaimer")

if show_disclaimer:
    st.markdown("""
    <div class="disclaimer-text">
    <h3>Prototype Version</h3>
    <p>This is a prototype version and may provide inaccurate information.</p>
    </div>
    """, unsafe_allow_html=True)

# Initialize session state
if "response_text" not in st.session_state:
    st.session_state.response_text = ""
if "translated_text" not in st.session_state:
    st.session_state.translated_text = ""
if "current_language" not in st.session_state:
    st.session_state.current_language = "english"
if "audio_file" not in st.session_state:
    st.session_state.audio_file = ""

# Use st.form to handle input submission
with st.form("disease_form"):
    # Input for disease name with capitalized first letter
    disease_name = st.text_input("Enter disease name:", value="", key="disease_name").strip().capitalize()
    submit_button = st.form_submit_button("Submit")

    if submit_button:
        if disease_name:
            # Call the function to query Pinecone and generate content
            st.session_state.response_text = query_and_generate_content(disease_name)
            st.session_state.translated_text = ""  # Reset translated text
            st.session_state.current_language = "english"
            st.session_state.audio_file = generate_audio(st.session_state.response_text)  # Generate audio
        else:
            st.error("Please enter a disease name.")

# Display the response and toggle button if there is content
if st.session_state.response_text:
    col1, col2 = st.columns([1, 2])

    with col1:
        if st.session_state.current_language == "english":
            if st.button("Convert to Hindi", key="convert_to_hindi"):
                st.session_state.translated_text = GoogleTranslator(source='auto', target='hi').translate(st.session_state.response_text)
                st.session_state.current_language = "hindi"
                st.session_state.audio_file = generate_audio(st.session_state.translated_text, 'hi')  # Generate audio
        else:
            if st.button("Convert to English", key="convert_to_english"):
                st.session_state.current_language = "english"
                st.session_state.audio_file = generate_audio(st.session_state.response_text)  # Generate audio

    with col2:
        if st.session_state.audio_file:
            audio_file_path = st.session_state.audio_file
            audio_bytes = open(audio_file_path, 'rb').read()
            st.audio(audio_bytes, format='audio/mp3')

    if st.session_state.current_language == "english":
        st.subheader("Information for Disease:")
        st.write(st.session_state.response_text)
    else:
        st.subheader("जानकारी (Information in Hindi):")
        st.write(st.session_state.translated_text)
