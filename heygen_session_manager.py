import os
import requests
import logging
from dotenv import load_dotenv
from utils.avatars import AVATAR_NAME_IDS, AVATAR_VOICE_IDS


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load the environment variables
load_dotenv()
HEYGEN_API_KEY = os.getenv("HEYGEN_API_KEY")
HEYGEN_SERVER_URL = os.getenv("HEYGEN_SERVER_URL")


def update_status(existing_status, new_message):
    """
    Simple helper to append a new status message to an existing one.
    """
    return existing_status + new_message + "<br>"

def create_new_session(avatar_name, status):
    """
    Creates a new streaming session with the Heygen API.
    """
    avatar_id = AVATAR_NAME_IDS.get(avatar_name)
    voice_id = AVATAR_VOICE_IDS.get(avatar_name)

    if not avatar_name or not voice_id:
        status = update_status(status, "No avatar or voice selected. Please select them first.")
        return None, None, status

    print(f"Avatar ID: {avatar_id}, Voice ID: {voice_id}")

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
            status = update_status(status, "Session created successfully. Click 'Start Session' to begin streaming.")
            return data, False, status
        else:
            status = update_status(status, f"Error creating session: {response.status_code} - {response.text}")
            return None, None, status

    except Exception as e:
        logger.exception("Exception during session creation.")
        status = update_status(status, f"Exception occurred: {e}")
        return None, None, status

def start_and_display_session(session_info, status):
    """
    Starts the session (via the streaming.start endpoint) and returns an HTML block
    that sets up the RTCPeerConnection using the sdp/ice data from Heygen.
    """
    if not session_info:
        status = update_status(status, "Please create a session first.")
        return None, True, status

    session_id = session_info["session_id"]
    sdp = session_info["sdp"]["sdp"]
    ice_servers = session_info["ice_servers2"]

    # Generate HTML + JS snippet to embed a live video stream
    video_html = f"""
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

    status = update_status(status, "Session started.")
    return video_html, True, status

def send_task(session_info, question, status):
    """
    Sends TTS text (or any text) to the Heygen streaming task endpoint.
    """
    if not session_info:
        status = update_status(status, "Please create a session first.")
        return status
    if not question:
        status = update_status(status, "Task input is empty.")
        return status

    session_id = session_info["session_id"]

    try:
        response = requests.post(
            f"{HEYGEN_SERVER_URL}/v1/streaming.task",
            headers={"Content-Type": "application/json", "X-Api-Key": HEYGEN_API_KEY},
            json={"session_id": session_id, "text": question},
        )

        logger.debug(f"Task response: {response.status_code} - {response.text}")

        if response.status_code == 200:
            status = update_status(status, "Task sent successfully.")
        else:
            status = update_status(status, f"Error sending task: {response.status_code} - {response.text}")
        return status

    except Exception as e:
        logger.exception("Exception when sending task.")
        status = update_status(status, f"Exception occurred: {e}")
        return status

def close_session(session_info, status):
    """
    Closes an existing session.
    """
    if not session_info:
        status = update_status(status, "No session to close.")
        return None, False, None, status  # Return a cleared state

    session_id = session_info["session_id"]

    try:
        response = requests.post(
            f"{HEYGEN_SERVER_URL}/v1/streaming.stop",
            headers={"Content-Type": "application/json", "X-Api-Key": HEYGEN_API_KEY},
            json={"session_id": session_id},
        )

        logger.debug(f"Close session response: {response.status_code} - {response.text}")

        if response.status_code == 200:
            status = update_status(status, "Session closed successfully.")
            return None, False, None, status  # Clear out session_info, started flag, and video
        else:
            status = update_status(status, f"Error closing session: {response.status_code}")
            return session_info, True, None, status

    except Exception as e:
        logger.exception("Exception when closing session.")
        status = update_status(status, f"Exception occurred: {e}")
        return session_info, True, None, status