# TTS Fallback Solution

## Current Status ✅

**Good News**: Your frontend error handling is working correctly! The error message from the backend is being properly parsed and displayed.

**Issue**: Edge TTS audio streaming is blocked by network/proxy settings, causing 500 errors.

## Solution: Graceful Fallback

Since TTS is currently unavailable due to network restrictions, implement a graceful fallback that:
1. Detects TTS failures
2. Shows a user-friendly message
3. Optionally disables TTS feature temporarily
4. Allows users to continue using the app

## Frontend Implementation

### Option 1: Disable TTS Feature Temporarily

```typescript
// api.ts or config.ts
export const TTS_ENABLED = false; // Set to false until network issue is resolved

// In your component
const handleSpeak = async (text: string) => {
  if (!TTS_ENABLED) {
    console.log('TTS is currently disabled due to network restrictions');
    // Optionally show a toast/notification
    // toast.info('Text-to-speech is temporarily unavailable');
    return;
  }
  
  try {
    const audioBlob = await textToSpeech(text);
    // ... play audio
  } catch (error) {
    // Error handling
  }
};
```

### Option 2: Graceful Error Handling with Retry

```typescript
// api.ts
export async function textToSpeech(
  text: string,
  voice?: string,
  retries: number = 0
): Promise<Blob> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/tts/text-to-voice`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, voice }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      const errorMessage = errorData.detail || 'TTS generation failed';
      
      // Check if it's a network/proxy error
      if (errorMessage.includes('proxy') || 
          errorMessage.includes('network') || 
          errorMessage.includes('firewall')) {
        // Don't retry for network issues
        throw new Error('TTS service unavailable due to network restrictions');
      }
      
      throw new Error(errorMessage);
    }

    return await response.blob();
  } catch (error) {
    // Log error but don't crash the app
    console.error('TTS error:', error);
    throw error;
  }
}
```

### Option 3: User-Friendly Error UI

```typescript
// AINose.tsx or your component
import { useState } from 'react';

function AINose() {
  const [ttsError, setTtsError] = useState<string | null>(null);
  const [ttsDisabled, setTtsDisabled] = useState(false);

  const handleSpeak = async (text: string) => {
    // Skip if TTS is disabled
    if (ttsDisabled) {
      return;
    }

    try {
      setTtsError(null);
      const audioBlob = await textToSpeech(text);
      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);
      
      audio.onended = () => URL.revokeObjectURL(audioUrl);
      audio.onerror = () => {
        URL.revokeObjectURL(audioUrl);
        setTtsError('فشل في تشغيل الصوت');
      };
      
      await audio.play();
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Unknown error';
      
      // Check if it's a network/proxy error
      if (errorMsg.includes('proxy') || 
          errorMsg.includes('network') || 
          errorMsg.includes('firewall') ||
          errorMsg.includes('blocked')) {
        setTtsError('خدمة تحويل النص إلى صوت غير متاحة حالياً بسبب قيود الشبكة');
        // Optionally disable TTS for this session
        setTtsDisabled(true);
      } else {
        setTtsError('فشل في توليد الصوت. يرجى المحاولة مرة أخرى.');
      }
    }
  };

  return (
    <div>
      {/* Your component content */}
      
      {/* TTS Error Banner */}
      {ttsError && (
        <div className="tts-error-banner" style={{
          padding: '12px',
          backgroundColor: '#fff3cd',
          border: '1px solid #ffc107',
          borderRadius: '4px',
          marginBottom: '16px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <span>{ttsError}</span>
          <button 
            onClick={() => {
              setTtsError(null);
              setTtsDisabled(false);
            }}
            style={{ marginLeft: '12px' }}
          >
            إعادة المحاولة
          </button>
        </div>
      )}
      
      {/* Disable TTS button if needed */}
      {ttsDisabled && (
        <button onClick={() => setTtsDisabled(false)}>
          تفعيل تحويل النص إلى صوت
        </button>
      )}
    </div>
  );
}
```

### Option 4: Check TTS Availability on App Start

```typescript
// hooks/useTTSAvailability.ts
import { useState, useEffect } from 'react';

export function useTTSAvailability() {
  const [isAvailable, setIsAvailable] = useState<boolean | null>(null);
  const [isChecking, setIsChecking] = useState(true);

  useEffect(() => {
    checkTTSAvailability();
  }, []);

  const checkTTSAvailability = async () => {
    setIsChecking(true);
    try {
      // Try a simple TTS request
      const response = await fetch(`${API_BASE_URL}/api/tts/text-to-voice`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: 'test' }),
      });

      setIsAvailable(response.ok);
    } catch (error) {
      setIsAvailable(false);
    } finally {
      setIsChecking(false);
    }
  };

  return { isAvailable, isChecking, checkAvailability: checkTTSAvailability };
}

// Usage in component
function AINose() {
  const { isAvailable, isChecking } = useTTSAvailability();

  if (isChecking) {
    return <div>Checking TTS availability...</div>;
  }

  return (
    <div>
      {!isAvailable && (
        <div className="warning">
          Text-to-speech is currently unavailable. You can still use all other features.
        </div>
      )}
      
      {/* Your component */}
      <button 
        onClick={() => handleSpeak(text)}
        disabled={!isAvailable}
      >
        Speak
      </button>
    </div>
  );
}
```

## Backend: Add Health Check Endpoint

Add a lightweight endpoint to check TTS availability:

```python
# app/routers/tts.py
@router.get("/health")
async def tts_health_check():
    """
    Check if TTS service is available.
    Returns status without actually generating audio.
    """
    try:
        # Try to list voices (lightweight check)
        voices = await edge_tts.list_voices()
        return {
            "status": "available",
            "voices_count": len(voices),
            "message": "TTS service is available"
        }
    except Exception as e:
        logger.error(f"TTS health check failed: {str(e)}")
        return {
            "status": "unavailable",
            "message": "TTS service is currently unavailable",
            "error": str(e)
        }
```

Then check from frontend:

```typescript
// Check TTS health
async function checkTTSHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/tts/health`);
    const data = await response.json();
    return data.status === 'available';
  } catch {
    return false;
  }
}
```

## Recommended Approach

For now, implement **Option 3** (User-Friendly Error UI) because:
1. ✅ Error handling is already working
2. ✅ Users get clear feedback
3. ✅ App continues to work
4. ✅ Easy to re-enable when network issue is fixed

## Testing Network Fix

To test if the network issue is resolved:

```bash
# Test from different network
# 1. Try mobile hotspot
# 2. Try different WiFi network
# 3. Test from a server/VPS without proxy

# Test TTS directly
curl -X POST "http://localhost:8000/api/tts/text-to-voice" \
  -H "Content-Type: application/json" \
  -d '{"text": "test"}' \
  -o test.mp3

# If it works, you'll get an MP3 file
file test.mp3
```

## Summary

1. ✅ **Frontend error handling is working correctly**
2. ⚠️ **TTS is blocked by network/proxy** (not a code issue)
3. ✅ **Implement graceful fallback** (Option 3 recommended)
4. 🔄 **Test from different network** when possible
5. 📝 **Document the limitation** for users

The app can function without TTS - it's a nice-to-have feature, not critical functionality.

