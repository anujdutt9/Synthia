import logging
from pathlib import Path
from streamlit.components.v1 import html
import streamlit as st
from streamlit_pdf_viewer import pdf_viewer
from utils.avatars import AVATAR_CHOICES
from heygen_session_manager import (
    create_new_session,
    start_and_display_session,
    send_task,
    close_session
)
from utils.pdf_utils import (
    get_pdf_text,
    get_chunks_from_text,
    get_text_embeddings,
    get_relevant_chunks
)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Streamlit Page Configuration
st.set_page_config(page_title="Synthia", layout="wide")

# State Initialization
if "session_info" not in st.session_state:
    st.session_state.session_info = None
if "video_html" not in st.session_state:
    st.session_state.video_html = None
if "session_started" not in st.session_state:
    st.session_state.session_started = False
if "status" not in st.session_state:
    st.session_state.status = ""
if "selected_avatar" not in st.session_state:
    st.session_state.selected_avatar = AVATAR_CHOICES[0]
if "pdf_path" not in st.session_state:
    st.session_state.pdf_path = None
if "pdf_bytes" not in st.session_state:
    st.session_state.pdf_bytes = None
if "pdf_name" not in st.session_state:
    st.session_state.pdf_name = None

# Step 1: Upload the PDF
if st.session_state.pdf_bytes is None:
    st.title("Chat with Synthia")
    st.subheader("Document Viewer")

    # Let user upload a PDF
    uploaded_pdf = st.file_uploader("Upload a PDF", type=["pdf"])

    if uploaded_pdf is not None:
        # Read once and store bytes in session state
        st.session_state.pdf_name = uploaded_pdf.name
        pdf_bytes = uploaded_pdf.read()
        if len(pdf_bytes) == 0:
            st.error("The uploaded PDF file is empty. Please upload a valid file.")
        else:
            st.session_state.pdf_bytes = pdf_bytes
            st.session_state.pdf_path = "temp_uploaded_file.pdf"
            st.experimental_rerun()
    else:
        st.info("No PDF uploaded yet. Please select a file above.")

# Step 2: Display the full app layout once the PDF is uploaded
else:
    st.title("Chat with Synthia: Your Interactive AI Assistant")
    left_col, right_col = st.columns([1, 1])

    # Write the uploaded PDF bytes to disk
    temp_pdf_path = st.session_state.pdf_name
    with open(temp_pdf_path, "wb") as temp_file:
        temp_file.write(st.session_state.pdf_bytes)

    # Ensure the file exists and is valid before processing
    temp_pdf_file = Path(temp_pdf_path)
    if not temp_pdf_file.exists() or temp_pdf_file.stat().st_size == 0:
        st.error("The uploaded PDF file is empty or missing. Please re-upload the file.")
    else:
        fpath_pdf = Path(temp_pdf_file)
        text = get_pdf_text(fpath_pdf)
        chunks = get_chunks_from_text(text)
        store_name = fpath_pdf.name.split('.')[0]
        fpath_index = Path(f"{store_name}.faiss")
        vectorstores = get_text_embeddings(fpath_pdf, chunks, fpath_index)

        # Left column: PDF viewer
        with left_col:
            # App layout with sidebar and main chat area
            st.subheader("Document Viewer")

            # Display the uploaded PDF in the sidebar
            with open(temp_pdf_path, "wb") as temp_file:
                temp_file.write(st.session_state.pdf_bytes)
            pdf_viewer(input=temp_pdf_path, width=800, height=800, key="pdf_viewer_sidebar")

        # Right column: Avatar selection + Video + Text input + Buttons
        with right_col:
            # Avatar Selection (Radio Buttons)
            st.subheader("Select an Avatar")
            avatar_names = [a["name"] for a in AVATAR_CHOICES]
            default_index = avatar_names.index(st.session_state.selected_avatar["name"])
            chosen_avatar_name = st.radio(
                "", avatar_names, index=default_index, key="avatar_selector", horizontal=True
            )

            # Update state whenever a new avatar is chosen
            if chosen_avatar_name != st.session_state.selected_avatar["name"]:
                for a in AVATAR_CHOICES:
                    if a["name"] == chosen_avatar_name:
                        st.session_state.selected_avatar = a
                        break

            # Display the video session
            st.subheader("Video Stream")
            if st.session_state.session_started and st.session_state.video_html:
                # Render the video HTML
                html(st.session_state.video_html, height=400)
            elif not st.session_state.session_started:
                st.info("No active video session. Start a session below!")

            # Buttons for session control
            st.subheader("Session Controls")
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                if st.button("Create Session"):
                    avatar_info = st.session_state.selected_avatar
                    create_new_session(avatar_info["avatar"], avatar_info["voice"])
            with col2:
                if st.button("Start Session"):
                    start_and_display_session()
                    st.session_state.pdf_path = "temp_uploaded_file.pdf"
            with col3:
                if st.button("Close Session"):
                    close_session()

            # Textbox for user input
            st.subheader("Ask a Question")
            question_text = st.text_input(
                "Type your question here:", placeholder="Enter your question", key="question_input"
            )

            # Get relevant chunks based on the question
            relevant_chunks = get_relevant_chunks(question_text, vectorstores)

            # Submit button for sending the question
            if st.button("Submit Question"):
                if question_text.strip():
                    send_task(question_text, relevant_chunks)
                else:
                    st.warning("Please enter a question before submitting.")