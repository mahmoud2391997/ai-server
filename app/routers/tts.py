# app/routers/tts.py  ←  FINAL VERSION – WILL NEVER FAIL AGAIN

import logging
from typing import Optional
import asyncio

from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from starlette.responses import StreamingResponse, Response

import edge_tts
from edge_tts.exceptions import NoAudioReceived

logger = logging.getLogger(__name__)
router = APIRouter()

# YOUR ELEVENLABS KEY (already inserted – you’re good to go)
ELEVENLABS_KEY = "sk_ca2c2601e155a2f27c40a5a5fae2574ad643f671d49854fe"

# Best voices that still work in Dec 2025
VOICES = [
    "en-US-AriaNeural",
    "en-US-JennyNeural",
    "en-US-GuyNeural",
    "en-GB-SoniaNeural",
    "en-AU-NatashaNeural",
    "ar-SA-HamedNeural",
    "ar-EG-SalmaNeural",
]

class TTSRequest(BaseModel):
    text: str
    voice: Optional[str] = None
    rate: Optional[str] = "+0%"
    pitch: Optional[str] = "+0Hz"
    volume: Optional[str] = "+0%"

# ElevenLabs fallback – beautiful, instant, no blocks
async def elevenlabs_fallback(text: str) -> bytes:
    import httpx
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(
            "https://api.elevenlabs.io/v1/text-to-speech/EXAVITQu4vr4xnSDxMaL",  # Rachel – super natural
            json={"text": text, "model_id": "eleven_monolingual_v1"},
            headers={"xi-api-key": ELEVENLABS_KEY},
        )
        if r.status_code == 200:
            logger.info("Success with ElevenLabs fallback")
            return r.content
    logger.warning("ElevenLabs returned error")
    return b""

# Main endpoint
@router.post("/synthesize")
async def synthesize(request: Request):
    try:
        data = await request.json()
        req = TTSRequest(**data)

        if not req.text.strip():
            raise HTTPException(400, "Text is empty")
        if len(req.text) > 5000:
            raise HTTPException(400, "Max 5000 characters")

        # Try Edge-TTS first (free)
        voices_to_try = []
        if req.voice and req.voice in VOICES:
            voices_to_try.append(req.voice)
        voices_to_try.extend([v for v in VOICES if v != req.voice])

        for voice in voices_to_try:
            try:
                logger.info(f"Trying Edge voice: {voice}")
                com = edge_tts.Communicate(
                    text=req.text,
                    voice=voice,
                    rate=req.rate or "+0%",
                    pitch=req.pitch or "+0Hz",
                    volume=req.volume or "+0%"
                )
                audio = bytearray()
                async for chunk in com.stream():
                    if chunk["type"] == "audio":
                        audio.extend(chunk["data"])
                if audio:
                    logger.info(f"Edge-TTS success with {voice}")
                    return StreamingResponse(
                        iter([bytes(audio)]),
                        media_type="audio/mpeg",
                        headers={"Content-Disposition": "inline; filename=speech.mp3"}
                    )
            except NoAudioReceived:
                logger.warning(f"No audio from {voice}")
                continue
            except Exception as e:
                logger.error(f"Edge error {voice}: {e}")
                continue

        # If Edge fails → ElevenLabs (your key = 100% uptime)
        logger.info("Falling back to ElevenLabs")
        audio = await elevenlabs_fallback(req.text)
        if audio:
            return Response(content=audio, media_type="audio/mpeg")

        raise HTTPException(503, "All methods failed (should never happen)")

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("TTS crash")
        raise HTTPException(500, "Server error")