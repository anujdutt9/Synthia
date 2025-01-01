import os
from dotenv import load_dotenv
import gradio as gr
from gradio_pdf import PDF
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
with gr.Blocks(theme=gr.themes.Ocean()) as demo:
    gr.Markdown("## 🎙️ Document Viewer and AI Assistant")
    # Instruction section
    instructions = gr.Markdown(
        "Upload a document to preview its content and ask a question related to it or just ask a random question."
    )
    with gr.Row():
        # Left panel for document upload and viewing
        with gr.Column(scale=5):
            pdf_view = PDF(label="Upload and View Document (Optional)", height=1000)

        # Right panel for user interaction and streaming video
        with gr.Column(scale=5):
            selected_avatar = gr.Radio(
                choices=AVATAR_NAMES,
                label="Select an Avatar to Assist You",
                value=AVATAR_NAMES[0],
            )
            user_question = gr.Textbox(
                label="Ask a Question",
                placeholder="Type your question here...",
                lines=2,
            )
            streaming_video = gr.Video(label="Live Video Stream", interactive=False)
            submit_btn = gr.Button("Submit Question")

    # Submit button event
    submit_btn.click(
        fn=process_request,
        inputs=[pdf_view, selected_avatar, user_question],
        outputs=[streaming_video],  # Update instructions or use other outputs to display results
    )


if __name__ == "__main__":
    demo.launch()
