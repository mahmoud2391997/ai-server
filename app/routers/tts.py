import logging
import os
from typing import Optional

from fastapi import APIRouter, Request, HTTPException, Response
from pydantic import BaseModel
from starlette.responses import StreamingResponse

import httpx
import edge_tts
from edge_tts.exceptions import NoAudioReceived

logger = logging.getLogger(__name__)

# -------------------------------------------------------------------
# GLOBAL SETTINGS
# -------------------------------------------------------------------

# Disable any system proxy (Edge TTS breaks if proxies exist)
os.environ.setdefault("NO_PROXY", "*")
os.environ.setdefault("no_proxy", "*")

# Force Edge TTS to use HTTP instead of WebSocket
os.environ["EDGE_TTS_TURN_OFF_WEBSOCKETS"] = "1"

# Use custom httpx client (NO PROXY)
client = httpx.AsyncClient(proxy=None)
edge_tts.Communicate.http_client = client

# -------------------------------------------------------------------
# ROUTER INIT
# -------------------------------------------------------------------
router = APIRouter()

SUPPORTED_VOICES = [
    "ar-SA-HamedNeural",
    "ar-SA-ZariyahNeural",
    "ar-AE-FarisNeural",
    "ar-EG-SalmaNeural",
    "ar-IQ-BasselNeural",
    "en-US-JennyNeural",
    "en-US-GuyNeural",
    "en-GB-LibbyNeural",
    "en-AU-NatashaNeural",
    "en-IN-NeerjaNeural"
]

GOOGLE_TTS_AVAILABLE = False   # Set to True if adding Google fallback


# -------------------------------------------------------------------
# Pydantic Model
# -------------------------------------------------------------------
class TTSRequest(BaseModel):
    text: str
    voice: Optional[str] = None
    rate: Optional[str] = "+0%"
    pitch: Optional[str] = "+0Hz"
    volume: Optional[str] = "+0%"


# -------------------------------------------------------------------
# Helper – Create Edge TTS Communicate object
# -------------------------------------------------------------------
def create_communicate(text: str, voice: str, rate: str, pitch: str, volume: str):
    """
    Create a clean edge_tts Communicate object
    with all proxy variables disabled temporarily.
    """
    old_env = {}

    proxy_keys = [
        "HTTP_PROXY", "http_proxy",
        "HTTPS_PROXY", "https_proxy",
        "ALL_PROXY", "all_proxy"
    ]

    # Remove proxy vars if they exist
    for key in proxy_keys:
        if key in os.environ:
            old_env[key] = os.environ[key]
            del os.environ[key]

    try:
        return edge_tts.Communicate(
            text=text,
            voice=voice,
            rate=rate,
            pitch=pitch,
            volume=volume
        )
    finally:
        # Restore proxy vars
        for key, val in old_env.items():
            os.environ[key] = val


# -------------------------------------------------------------------
# MAIN ROUTE – SYNTHESIZE TTS
# -------------------------------------------------------------------
@router.post("/synthesize")
async def synthesize_speech(request: Request):
    try:
        payload = await request.json()
        tts = TTSRequest(**payload)

        # ----------------------
        # VALIDATION
        # ----------------------
        if not tts.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")

        if len(tts.text) > 5000:
            raise HTTPException(status_code=400, detail="Maximum 5000 characters allowed.")

        primary_voice = tts.voice if tts.voice in SUPPORTED_VOICES else SUPPORTED_VOICES[0]

        rate = tts.rate or "+0%"
        pitch = tts.pitch or "+0Hz"
        volume = tts.volume or "+0%"

        # ----------------------
        # FUNCTION: Try voices
        # ----------------------
        async def synthesize():
            voices = [primary_voice] + [v for v in SUPPORTED_VOICES if v != primary_voice]

            for voice in voices:
                logger.info(f"Trying voice: {voice}")

                try:
                    com = create_communicate(tts.text, voice, rate, pitch, volume)

                    audio = bytearray()
                    async for chunk in com.stream():
                        if chunk["type"] == "audio":
                            audio.extend(chunk["data"])

                    if audio:
                        logger.info(f"✔ Audio received using {voice}")
                        return bytes(audio)

                    logger.warning(f"No audio from voice {voice}, trying next...")

                except NoAudioReceived:
                    logger.warning(f"NoAudioReceived: {voice}, trying next...")
                except Exception as e:
                    logger.error(f"Error using voice {voice}: {e}")
                    continue

            return None

        audio_bytes = await synthesize()

        # ----------------------
        # FALLBACK TO GOOGLE
       
        if audio_bytes is None:
            if GOOGLE_TTS_AVAILABLE:
                audio_content = synthesize_speech_google(tts.text)
                return Response(content=audio_content, media_type="audio/mpeg")

            raise HTTPException(status_code=500, detail="Failed to generate audio with all voices.")

        # ----------------------
        # SUCCESS RESPONSE
        # ----------------------
        return StreamingResponse(
            iter([audio_bytes]),
            media_type="audio/mpeg",
            headers={"Content-Disposition": "inline; filename=speech.mp3"}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"TTS error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
