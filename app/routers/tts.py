from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional
import edge_tts
import io

router = APIRouter()

class TTSRequest(BaseModel):
    text: str
    voice: Optional[str] = None  # Voice name (e.g., "ar-SA-HamedNeural" for Arabic)
    rate: Optional[str] = "+0%"  # Speech rate
    pitch: Optional[str] = "+0Hz"  # Voice pitch
    volume: Optional[str] = "+0%"  # Volume

@router.post("/text-to-voice")
@router.post("/synthesize")
async def synthesize_speech(request: TTSRequest):
    """
    Convert text to speech and return audio file.
    
    Args:
        request: TTSRequest containing text and optional voice settings
        
    Returns:
        Audio file (MP3 format) as binary response
    """
    try:
        # Validate text
        if not request.text or len(request.text.strip()) == 0:
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        # Limit text length to prevent abuse
        if len(request.text) > 5000:
            raise HTTPException(status_code=400, detail="Text too long. Maximum 5000 characters.")
        
        # Default to Arabic voice if not specified
        voice = request.voice or "ar-SA-HamedNeural"  # Arabic male voice
        
        # Generate speech
        communicate = edge_tts.Communicate(
            text=request.text,
            voice=voice,
            rate=request.rate,
            pitch=request.pitch,
            volume=request.volume
        )
        
        # Create in-memory buffer for audio
        audio_buffer = io.BytesIO()
        
        # Stream audio data to buffer
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_buffer.write(chunk["data"])
        
        # Get audio bytes
        audio_buffer.seek(0)
        audio_bytes = audio_buffer.read()
        
        # Return audio file
        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "attachment; filename=speech.mp3",
                "Content-Length": str(len(audio_bytes))
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS generation failed: {str(e)}")

@router.get("/voices")
async def list_voices(locale: Optional[str] = None):
    """
    List available voices for text-to-speech.
    
    Args:
        locale: Optional locale filter (e.g., "ar-SA" for Arabic)
        
    Returns:
        List of available voices
    """
    try:
        voices = await edge_tts.list_voices()
        
        # Filter by locale if provided
        if locale:
            voices = [v for v in voices if v["Locale"].startswith(locale)]
        
        return {
            "voices": voices,
            "count": len(voices)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list voices: {str(e)}")

@router.get("/voices/arabic")
async def list_arabic_voices():
    """
    List available Arabic voices.
    
    Returns:
        List of Arabic voices
    """
    try:
        voices = await edge_tts.list_voices()
        arabic_voices = [v for v in voices if v["Locale"].startswith("ar-")]
        
        return {
            "voices": arabic_voices,
            "count": len(arabic_voices),
            "recommended": {
                "male": "ar-SA-HamedNeural",
                "female": "ar-SA-ZariyahNeural"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list Arabic voices: {str(e)}")

