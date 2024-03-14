import logging
import queue
import threading
import time
import urllib.request
import os
from pathlib import Path
import pyaudio
import streamlit as st
from google.cloud import speech_v1p1beta1 as speech
from twilio.rest import Client

HERE = Path(__file__).parent

logger = logging.getLogger(__name__)

def download_file(url, download_to: Path, expected_size=None):
    if download_to.exists():
        if expected_size:
            if download_to.stat().st_size == expected_size:
                return
        else:
            st.info(f"{url} is already downloaded.")
            if not st.button("Download again?"):
                return

    download_to.parent.mkdir(parents=True, exist_ok=True)

    weights_warning, progress_bar = None, None
    try:
        weights_warning = st.warning("Downloading %s..." % url)
        progress_bar = st.progress(0)
        with open(download_to, "wb") as output_file:
            with urllib.request.urlopen(url) as response:
                length = int(response.info()["Content-Length"])
                counter = 0.0
                MEGABYTES = 2.0 ** 20.0
                while True:
                    data = response.read(8192)
                    if not data:
                        break
                    counter += len(data)
                    output_file.write(data)
                    weights_warning.warning(
                        "Downloading %s... (%6.2f/%6.2f MB)"
                        % (url, counter / MEGABYTES, length / MEGABYTES)
                    )
                    progress_bar.progress(min(counter / length, 1.0))
    finally:
        if weights_warning is not None:
            weights_warning.empty()
        if progress_bar is not None:
            progress_bar.empty()

@st.cache_data
def get_ice_servers():
    try:
        account_sid = os.environ["TWILIO_ACCOUNT_SID"]
        auth_token = os.environ["TWILIO_AUTH_TOKEN"]
    except KeyError:
        logger.warning(
            "Twilio credentials are not set. Fallback to a free STUN server from Google."
        )
        return [{"urls": ["stun:stun.l.google.com:19302"]}]

    client = Client(account_sid, auth_token)
    token = client.tokens.create()
    return token.ice_servers

def audio_thread(audio_queue):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    while True:
        audio_data = stream.read(CHUNK)
        audio_queue.put(audio_data)

def main():
    st.header("Real Time Speech-to-Text")
    st.markdown(
        """
This demo app is using [Google Cloud Speech-to-Text](https://cloud.google.com/speech-to-text),
an open speech-to-text engine.
"""
    )

    app_sst()

def app_sst():
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:\\Users\\manav\\Downloads\\nth-rookery-417118-b3f039c25f9c.json"
    
    audio_queue = queue.Queue()
    audio_thread_instance = threading.Thread(target=audio_thread, args=(audio_queue,), daemon=True)
    audio_thread_instance.start()

    client = speech.SpeechClient()

    start_button = st.button("Start Talking")
    if start_button:
        while True:
            try:
                audio_data = audio_queue.get(block=True, timeout=1)
            except queue.Empty:
                continue

            response = client.recognize(
                audio={"content": audio_data},
                config={
                    "encoding": speech.RecognitionConfig.AudioEncoding.LINEAR16,
                    "sample_rate_hertz": 44100,  # Adjust as needed
                    "language_code": "en-US",
                },
            )

            for result in response.results:
                st.text(f"Transcription: {result.alternatives[0].transcript}")

if __name__ == "__main__":
    import os

    DEBUG = os.environ.get("DEBUG", "false").lower() not in ["false", "no", "0"]

    logging.basicConfig(
        format="[%(asctime)s] %(levelname)7s from %(name)s in %(pathname)s:%(lineno)d: "
        "%(message)s",
        force=True,
    )

    logger.setLevel(level=logging.DEBUG if DEBUG else logging.INFO)

    main()