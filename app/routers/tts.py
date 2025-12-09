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
import httpx

logger = logging.getLogger(__name__)

# Set NO_PROXY at module level to prevent edge_tts from using proxy
# This needs to be set before edge_tts initializes its HTTP client
os.environ.setdefault('NO_PROXY', '*')
os.environ.setdefault('no_proxy', '*')

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
        logger.info(f"Current proxy env vars: HTTP_PROXY={os.environ.get('HTTP_PROXY', 'None')}, HTTPS_PROXY={os.environ.get('HTTPS_PROXY', 'None')}")
        
        # Create httpx client without proxy for edge_tts
        # edge_tts uses httpx internally, so we need to ensure no proxy is used
        # Temporarily unset proxy env vars and use a custom httpx client if possible
        old_proxy_vars = {}
        proxy_vars = ['HTTP_PROXY', 'http_proxy', 'HTTPS_PROXY', 'https_proxy', 'ALL_PROXY', 'all_proxy']
        
        # Save and unset proxy variables
        for var in proxy_vars:
            if var in os.environ:
                old_proxy_vars[var] = os.environ[var]
                logger.info(f"Unsetting proxy var: {var}={os.environ[var]}")
                del os.environ[var]
        
        logger.info(f"After unsetting proxies, NO_PROXY={os.environ.get('NO_PROXY', 'None')}")
        
        try:
            # Generate speech using edge_tts
            # The NO_PROXY set at module level should help, but we also ensure proxy vars are unset
            logger.info("Creating edge_tts.Communicate object...")
            communicate = edge_tts.Communicate(
                text=request.text,
                voice=voice,
                rate=request.rate or "+0%",
                pitch=request.pitch or "+0Hz",
                volume=request.volume or "+0%"
            )
            logger.info("edge_tts.Communicate object created successfully")
        except Exception as comm_error:
            logger.exception(f"Error creating Communicate object: {type(comm_error).__name__}: {str(comm_error)}")
            raise
        finally:
            # Restore proxy environment variables
            for var, value in old_proxy_vars.items():
                os.environ[var] = value
                logger.info(f"Restored proxy var: {var}")
        
        # Use temporary file for save() method (it requires a file path)
        temp_path = None
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                temp_path = temp_file.name
            
            # Save audio to temporary file
            logger.info(f"Saving audio to temp file: {temp_path}")
            try:
                await communicate.save(temp_path)
                logger.info("Audio save() completed")
            except Exception as save_error:
                logger.exception(f"Error in communicate.save(): {type(save_error).__name__}: {str(save_error)}")
                logger.error(f"Full traceback for save error:")
                import traceback
                logger.error(traceback.format_exc())
                raise
            
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
            logger.error("=" * 60)
            logger.error("TTS ERROR: NoAudioReceived")
            logger.error("=" * 60)
            logger.error(f"Error message: {str(e)}")
            logger.error(f"Text: {request.text[:50]}...")
            logger.error(f"Voice: {voice}")
            logger.error(f"Rate: {request.rate}, Pitch: {request.pitch}, Volume: {request.volume}")
            logger.error("")
            logger.error("This error occurs when:")
            logger.error("1. Edge TTS service is reachable (can get metadata)")
            logger.error("2. But the audio streaming connection is blocked")
            logger.error("")
            logger.error("Common causes:")
            logger.error("- Proxy/firewall blocking WebSocket or streaming connections")
            logger.error("- Network restrictions on specific Edge TTS endpoints")
            logger.error("- Corporate firewall blocking audio streaming")
            logger.error("")
            logger.error("Current environment:")
            logger.error(f"  NO_PROXY: {os.environ.get('NO_PROXY', 'Not set')}")
            logger.error(f"  HTTP_PROXY: {os.environ.get('HTTP_PROXY', 'Not set')}")
            logger.error(f"  HTTPS_PROXY: {os.environ.get('HTTPS_PROXY', 'Not set')}")
            logger.error("=" * 60)
            # Clean up temp file if it exists
            if temp_path and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except:
                    pass
            raise HTTPException(
                status_code=500,
                detail="TTS service could not generate audio. The Edge TTS service is reachable but audio streaming is blocked. This is often caused by proxy or firewall settings. Please check your network configuration or contact your system administrator."
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

@router.get("/health")
async def tts_health_check():
    """
    Check if TTS service is available.
    This endpoint tests if Edge TTS can successfully generate audio.
    
    Returns:
        Health status with availability information
    """
    try:
        # Test 1: Can we list voices? (lightweight check)
        try:
            voices = await edge_tts.list_voices()
            voice_count = len(voices)
        except Exception as e:
            logger.error(f"Failed to list voices in health check: {str(e)}")
            return {
                "status": "unavailable",
                "available": False,
                "reason": "Cannot connect to Edge TTS service",
                "error": str(e),
                "can_list_voices": False
            }
        
        # Test 2: Can we actually generate audio? (more thorough check)
        try:
            # Try to generate a very short audio clip
            test_text = "test"
            communicate = edge_tts.Communicate(
                text=test_text,
                voice="ar-SA-HamedNeural",
                rate="+0%",
                pitch="+0Hz",
                volume="+0%"
            )
            
            # Try to stream audio (this is where it usually fails)
            audio_received = False
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_received = True
                    break  # We got at least one audio chunk, that's enough
            
            if audio_received:
                return {
                    "status": "available",
                    "available": True,
                    "message": "TTS service is fully operational",
                    "can_list_voices": True,
                    "voice_count": voice_count,
                    "can_generate_audio": True
                }
            else:
                return {
                    "status": "unavailable",
                    "available": False,
                    "reason": "Audio streaming is blocked (proxy/firewall issue)",
                    "can_list_voices": True,
                    "voice_count": voice_count,
                    "can_generate_audio": False,
                    "suggestion": "Check network/proxy settings or try from a different network"
                }
                
        except edge_tts.exceptions.NoAudioReceived:
            return {
                "status": "unavailable",
                "available": False,
                "reason": "Audio streaming is blocked",
                "can_list_voices": True,
                "voice_count": voice_count,
                "can_generate_audio": False,
                "suggestion": "This is often caused by proxy or firewall settings blocking the audio stream"
            }
        except Exception as e:
            logger.error(f"Failed to generate test audio in health check: {str(e)}")
            return {
                "status": "unavailable",
                "available": False,
                "reason": f"Audio generation failed: {str(e)}",
                "can_list_voices": True,
                "voice_count": voice_count,
                "can_generate_audio": False,
                "error": str(e)
            }
            
    except Exception as e:
        logger.exception(f"TTS health check failed: {str(e)}")
        return {
            "status": "unavailable",
            "available": False,
            "reason": "Health check failed",
            "error": str(e)
        }

