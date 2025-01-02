import os
from dotenv import load_dotenv
import gradio as gr
from gradio_pdf import PDF
from heygen_session_manager import create_new_session, start_and_display_session, send_task, close_session
from utils.avatars import AVATAR_NAMES


# Load the environment variables
load_dotenv()
HEYGEN_API_KEY = os.getenv("HEYGEN_API_KEY")


def process_request(document: str, selected_avatar: str, question: str) -> str:
    """
    Process the document and question using the Heygen API.
    """
    # Call the Heygen API to get the answer
    response = "This is a sample response from the Heygen API."
    return response

# Define the interface
# with gr.Blocks(theme=gr.themes.Ocean()) as demo:
    # gr.Markdown("## 🎙️ Document Viewer and AI Assistant")
    # # Instruction section
    # instructions = gr.Markdown(
    #     "Upload a document to preview its content and ask a question related to it or just ask a random question."
    # )
    # with gr.Row():
    #     # Left panel for document upload and viewing
    #     with gr.Column(scale=5):
    #         pdf_view = PDF(label="Upload and View Document (Optional)", height=1000)
    #
    #     # Right panel for user interaction and streaming video
    #     with gr.Column(scale=5):
    #         selected_avatar = gr.Radio(
    #             choices=AVATAR_NAMES,
    #             label="Select an Avatar to Assist You",
    #             value=AVATAR_NAMES[0],
    #         )
    #         user_question = gr.Textbox(
    #             label="Ask a Question",
    #             placeholder="Type your question here...",
    #             lines=2,
    #         )
    #         streaming_video = gr.Video(label="Live Video Stream", interactive=False)
    #         submit_btn = gr.Button("Submit Question")
    #
    # # Submit button event
    # submit_btn.click(
    #     fn=process_request,
    #     inputs=[pdf_view, selected_avatar, user_question],
    #     outputs=[streaming_video],  # Update instructions or use other outputs to display results
    # )

# Gradio App
with gr.Blocks(theme=gr.themes.Ocean()) as demo:
    gr.Markdown("## Heygen Streaming Demo")
    # Instruction section
    instructions = gr.Markdown(
        "Upload a document to generate a podcast based on its content, or leave it empty to generate a random story podcast based on the selected persona."
    )

    # States for storing session-related data
    session_info_state = gr.State()  # To store the session info dict
    session_started_state = gr.State()  # To store whether session has started (True/False)
    video_html_state = gr.State()  # To store the HTML snippet with video streaming
    status_state = gr.State(value="")  # For storing status messages

    with gr.Row():
        with gr.Column(scale=5):
            status_display = gr.HTML(label="Status Messages")
            video_display = gr.HTML(label="Live Video Stream")

        with gr.Column(scale=5):
            avatar_radio = gr.Radio(choices=AVATAR_NAMES, label="Select an Avatar", value=AVATAR_NAMES[0])
            create_button = gr.Button("Create Session")
            start_button = gr.Button("Start Session", variant="secondary")
            close_button = gr.Button("Close Session", variant="stop")

    question_input = gr.Textbox(label="Question/Text to Speak", placeholder="Enter your text...")
    send_task_button = gr.Button("Send Task")


    # -------------- BUTTON LOGIC ----------------
    def handle_create_session(avatar_id, status):
        session_info, started, status = create_new_session(avatar_id, status)
        return session_info, started, status


    create_button.click(
        fn=handle_create_session,
        inputs=[avatar_radio, status_state],
        outputs=[session_info_state, session_started_state, status_state],
    )


    def handle_start_session(session_info, status):
        vid_html, started, status = start_and_display_session(session_info, status)
        return started, vid_html, status


    start_button.click(
        fn=handle_start_session,
        inputs=[session_info_state, status_state],
        outputs=[session_started_state, video_html_state, status_state],
    )

    # Update the video_display whenever video_html_state is changed
    video_html_state.change(
        fn=lambda vid: vid,
        inputs=video_html_state,
        outputs=video_display
    )


    def handle_send_task(session_info, question, status):
        status = send_task(session_info, question, status)
        return status


    send_task_button.click(
        fn=handle_send_task,
        inputs=[session_info_state, question_input, status_state],
        outputs=[status_state],
    )


    def handle_close_session(session_info, status):
        new_sess_info, started, vid_html, status = close_session(session_info, status)
        return new_sess_info, started, vid_html, status


    close_button.click(
        fn=handle_close_session,
        inputs=[session_info_state, status_state],
        outputs=[session_info_state, session_started_state, video_html_state, status_state],
    )

    # Reflect status_state changes to the HTML
    status_state.change(
        fn=lambda s: s,
        inputs=status_state,
        outputs=status_display
    )

if __name__ == "__main__":
    demo.launch(debug=True)
