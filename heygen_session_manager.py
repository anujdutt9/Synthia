import os
import logging
import requests
from dotenv import load_dotenv
import streamlit as st
from assistant import get_assistant_response


load_dotenv()
HEYGEN_API_KEY = os.getenv("HEYGEN_API_KEY")
HEYGEN_SERVER_URL = os.getenv("HEYGEN_SERVER_URL")


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def update_status(message):
    st.markdown(f"**Status:** {message}")
    logger.info(message)

def create_new_session(avatar_id=None, voice_id=None):
    if avatar_id is None or voice_id is None:
        update_status("No avatar selected. Please select an avatar first.")
        return

    payload = {
        "quality": "low",
        "avatar_name": avatar_id,
        "voice": {"voice_id": voice_id}
    }

    try:
        response = requests.post(
            f"{HEYGEN_SERVER_URL}/v1/streaming.new",
            headers={"Content-Type": "application/json", "X-Api-Key": HEYGEN_API_KEY},
            json=payload,
        )

        logger.debug(f"Create session response: {response.status_code} - {response.text}")

        if response.status_code == 200:
            data = response.json()["data"]
            st.session_state.session_info = data
            update_status("Session created successfully. Click 'Start Session' to begin streaming.")
        else:
            update_status(f"Error creating session: {response.status_code} - {response.text}")
    except Exception as e:
        logger.exception("Exception during session creation.")
        update_status(f"Exception occurred: {e}")

def start_and_display_session():
    if not st.session_state.session_info:
        update_status("Please create a session first.")
        return

    session_id = st.session_state.session_info["session_id"]
    sdp = st.session_state.session_info["sdp"]["sdp"]
    ice_servers = st.session_state.session_info["ice_servers2"]

    st.session_state.video_html = f"""
    <video id="mediaElement" autoplay playsinline style="width: 100%; max-height: 400px; border: 1px solid #ccc;"></video>
    <div id="status" style="margin-top:10px; font-family: Arial, sans-serif;"></div>

    <script>
    const SERVER_URL = "{HEYGEN_SERVER_URL}";
    const API_KEY = "{HEYGEN_API_KEY}";
    const session_id = "{session_id}";
    const statusElement = document.getElementById('status');
    const mediaElement = document.getElementById('mediaElement');

    function updateStatus(msg) {{
        statusElement.innerHTML += msg + "<br>";
    }}

    const iceServers = {ice_servers};
    let peerConnection = new RTCPeerConnection({{ iceServers: iceServers }});

    peerConnection.ontrack = (event) => {{
        updateStatus("Received track");
        mediaElement.srcObject = event.streams[0];
    }};

    peerConnection.onicecandidate = async (event) => {{
        if (event.candidate) {{
            updateStatus("Sending ICE candidate...");
            const resp = await fetch(SERVER_URL + "/v1/streaming.ice", {{
                method: "POST",
                headers: {{
                    "Content-Type": "application/json",
                    "X-Api-Key": API_KEY
                }},
                body: JSON.stringify({{
                    session_id: session_id,
                    candidate: event.candidate.toJSON()
                }})
            }});
            if (!resp.ok) {{
                updateStatus("Failed to send ICE candidate");
            }} else {{
                updateStatus("ICE candidate sent.");
            }}
        }}
    }};

    peerConnection.oniceconnectionstatechange = () => {{
        updateStatus("ICE state: " + peerConnection.iceConnectionState);
    }};

    (async () => {{
        updateStatus("Setting remote description...");
        const remoteDescription = new RTCSessionDescription({{type: "offer", sdp: `{sdp}`}});
        await peerConnection.setRemoteDescription(remoteDescription);
        updateStatus("Remote desc set. Creating answer...");

        const localDescription = await peerConnection.createAnswer();
        await peerConnection.setLocalDescription(localDescription);

        updateStatus("Sending local SDP answer to server...");
        const resp = await fetch(SERVER_URL + "/v1/streaming.start", {{
            method: "POST",
            headers: {{
                "Content-Type": "application/json",
                "X-Api-Key": API_KEY
            }},
            body: JSON.stringify({{ session_id: session_id, sdp: localDescription }})
        }});

        if (resp.ok) {{
            updateStatus("Session started successfully!");
        }} else {{
            updateStatus("Failed to start session on server.");
            console.error(await resp.text());
        }}
    }})();
    </script>
    """

    st.session_state.session_started = True
    update_status("Session started.")

def send_task(question: str):
    if not st.session_state.session_info:
        update_status("Please create a session first.")
        return
    text = get_assistant_response(question)
    if not text:
        update_status("Task input is empty.")
        return

    session_id = st.session_state.session_info["session_id"]
    try:
        response = requests.post(
            f"{HEYGEN_SERVER_URL}/v1/streaming.task",
            headers={"Content-Type": "application/json", "X-Api-Key": HEYGEN_API_KEY},
            json={"session_id": session_id, "text": text},
        )

        logger.debug(f"Task response: {response.status_code} - {response.text}")

        if response.status_code == 200:
            update_status("Task sent successfully.")
        else:
            update_status(f"Error sending task: {response.status_code} - {response.text}")
    except Exception as e:
        logger.exception("Exception when sending task.")
        update_status(f"Exception occurred: {e}")

def close_session():
    if not st.session_state.session_info:
        update_status("No session to close.")
        return

    session_id = st.session_state.session_info["session_id"]

    try:
        response = requests.post(
            f"{HEYGEN_SERVER_URL}/v1/streaming.stop",
            headers={"Content-Type": "application/json", "X-Api-Key": HEYGEN_API_KEY},
            json={"session_id": session_id},
        )

        logger.debug(f"Close session response: {response.status_code} - {response.text}")

        if response.status_code == 200:
            update_status("Session closed successfully.")
            st.session_state.session_info = None
            st.session_state.session_started = False
            st.session_state.video_html = None
        else:
            update_status(f"Error closing session: {response.status_code}")
    except Exception as e:
        logger.exception("Exception when closing session.")
        update_status(f"Exception occurred: {e}")