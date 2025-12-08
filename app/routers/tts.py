from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional
import logging
import edge_tts
import edge_tts.exceptions
import io
import tempfile
import os

logger = logging.getLogger(__name__)

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
        logger.info(f"TTS request received: text length={len(request.text)}, voice={request.voice}")
        
        # Validate text
        if not request.text or len(request.text.strip()) == 0:
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        # Limit text length to prevent abuse
        if len(request.text) > 5000:
            raise HTTPException(status_code=400, detail="Text too long. Maximum 5000 characters.")
        
        # Default to Arabic voice if not specified
        voice = request.voice or "ar-SA-HamedNeural"  # Arabic male voice
        
        logger.info(f"Generating speech with voice: {voice}")
        
        # Generate speech using edge_tts
        communicate = edge_tts.Communicate(
            text=request.text,
            voice=voice,
            rate=request.rate or "+0%",
            pitch=request.pitch or "+0Hz",
            volume=request.volume or "+0%"
        )
        
        # Use temporary file for save() method (it requires a file path)
        temp_path = None
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                temp_path = temp_file.name
            
            # Save audio to temporary file
            await communicate.save(temp_path)
            
            # Read audio bytes from file
            with open(temp_path, 'rb') as f:
                audio_bytes = f.read()
            
            # Clean up temporary file
            try:
                if temp_path and os.path.exists(temp_path):
                    os.unlink(temp_path)
            except:
                pass
            
            if len(audio_bytes) == 0:
                logger.error("Audio file is empty after save()")
                raise HTTPException(
                    status_code=500,
                    detail="Generated audio is empty. Please try again or use different parameters."
                )
            
            logger.info(f"TTS generation successful: {len(audio_bytes)} bytes")
            
        except edge_tts.exceptions.NoAudioReceived as e:
            logger.error(f"edge_tts NoAudioReceived error: {str(e)}")
            # Clean up temp file if it exists
            if temp_path and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except:
                    pass
            raise HTTPException(
                status_code=500,
                detail="TTS service could not generate audio. This may be due to network issues or service unavailability. Please try again later."
            )
        except Exception as tts_error:
            logger.exception(f"Error during TTS generation: {str(tts_error)}")
            # Clean up temp file if it exists
            if temp_path and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except:
                    pass
            raise HTTPException(
                status_code=500,
                detail=f"TTS generation failed: {str(tts_error)}"
            )
        
        # Return audio file
        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "attachment; filename=speech.mp3",
                "Content-Length": str(len(audio_bytes))
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"TTS generation failed: {str(e)}")
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

