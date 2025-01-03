import logging
from streamlit.components.v1 import html
import streamlit as st
from streamlit_pdf_viewer import pdf_viewer
from utils.avatars import AVATAR_CHOICES
from heygen_session_manager import create_new_session, start_and_display_session, send_task, close_session


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Streamlit Page Configuration
st.set_page_config(page_title="Heygen Streaming Demo", layout="wide")

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
    # Default to the first avatar in the list
    st.session_state.selected_avatar = AVATAR_CHOICES[0]

# Layout
st.title("Synthia")

left_col, right_col = st.columns([1, 1])

# Left column: PDF viewer
with left_col:
    st.subheader("Document Viewer")
    # Let user upload a PDF
    uploaded_pdf = st.file_uploader("Upload a PDF", type=["pdf"])

    if uploaded_pdf is not None:
        # Save the uploaded file to a temporary location
        temp_pdf_path = "temp_uploaded_file.pdf"
        with open(temp_pdf_path, "wb") as temp_file:
            temp_file.write(uploaded_pdf.read())

        # Display the PDF in the viewer
        pdf_viewer(input=temp_pdf_path, width=1000, height=600, key="pdf_viewer_uploaded")
    else:
        st.info("No PDF uploaded yet. Please select a file above.")

# Right column: Avatar selection + Video + Text input + Buttons
with right_col:
    st.subheader("Streaming Controller")

    # Avatar Selection (Radio Buttons)
    avatar_names = [a["name"] for a in AVATAR_CHOICES]
    default_index = avatar_names.index(st.session_state.selected_avatar["name"])
    chosen_avatar_name = st.radio("Select an Avatar", avatar_names, index=default_index)

    # Update state whenever a new avatar is chosen
    if chosen_avatar_name != st.session_state.selected_avatar["name"]:
        for a in AVATAR_CHOICES:
            if a["name"] == chosen_avatar_name:
                st.session_state.selected_avatar = a
                break
    # Text input below the video
    question_text = st.text_input("Enter your question/text:", key="question_input")

    # Buttons for session control
    create_btn, start_btn, send_btn, close_btn = st.columns([1,1,1,1])

    with create_btn:
        if st.button("Create Session"):
            avatar_info = st.session_state.selected_avatar
            create_new_session(avatar_info["avatar"], avatar_info["voice"])

    with start_btn:
        if st.button("Start Session"):
            start_and_display_session()

    with send_btn:
        if st.button("Send Task"):
            send_task(question_text)

    with close_btn:
        if st.button("Close Session"):
            close_session()

    # Display the video HTML if session started
    if st.session_state.video_html and st.session_state.session_started:
        html(st.session_state.video_html, height=600)
    else:
        st.info("No active video session.")

    # Display status messages at the bottom
    st.markdown(
        f"<div style='max-height:150px; overflow-y:auto; border:1px solid #ccc; padding:10px;'>{st.session_state.status}</div>",
        unsafe_allow_html=True
    )
