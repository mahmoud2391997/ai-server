# Frontend TTS Health Check Implementation

## Problem
The TTS endpoint is returning 500 errors due to network/proxy blocking. Instead of showing errors to users, we should check TTS availability first and gracefully handle unavailability.

## Solution: Add Health Check

### 1. Backend Health Check Endpoint ✅

The backend now has a `/api/tts/health` endpoint that checks:
- Can list voices? (lightweight check)
- Can generate audio? (thorough check)

**Endpoint**: `GET /api/tts/health`

**Response when available**:
```json
{
  "status": "available",
  "available": true,
  "message": "TTS service is fully operational",
  "can_list_voices": true,
  "voice_count": 32,
  "can_generate_audio": true
}
```

**Response when unavailable**:
```json
{
  "status": "unavailable",
  "available": false,
  "reason": "Audio streaming is blocked",
  "can_list_voices": true,
  "voice_count": 32,
  "can_generate_audio": false,
  "suggestion": "This is often caused by proxy or firewall settings blocking the audio stream"
}
```

### 2. Frontend Implementation

#### Option A: Check on App Start (Recommended)

```typescript
// hooks/useTTSAvailability.ts
import { useState, useEffect } from 'react';

interface TTSHealthStatus {
  available: boolean;
  status: string;
  reason?: string;
  can_generate_audio?: boolean;
}

export function useTTSAvailability() {
  const [healthStatus, setHealthStatus] = useState<TTSHealthStatus | null>(null);
  const [isChecking, setIsChecking] = useState(true);

  useEffect(() => {
    checkTTSHealth();
  }, []);

  const checkTTSHealth = async () => {
    setIsChecking(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/tts/health`);
      const data = await response.json();
      setHealthStatus(data);
    } catch (error) {
      setHealthStatus({
        available: false,
        status: 'unavailable',
        reason: 'Failed to check TTS health'
      });
    } finally {
      setIsChecking(false);
    }
  };

  return {
    isAvailable: healthStatus?.available ?? false,
    healthStatus,
    isChecking,
    refresh: checkTTSHealth
  };
}
```

#### Option B: Check Before Each TTS Call

```typescript
// api.ts
let ttsAvailabilityCache: { available: boolean; checkedAt: number } | null = null;
const TTS_CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

async function checkTTSAvailability(): Promise<boolean> {
  // Check cache first
  if (ttsAvailabilityCache) {
    const age = Date.now() - ttsAvailabilityCache.checkedAt;
    if (age < TTS_CACHE_DURATION) {
      return ttsAvailabilityCache.available;
    }
  }

  try {
    const response = await fetch(`${API_BASE_URL}/api/tts/health`);
    const data = await response.json();
    
    ttsAvailabilityCache = {
      available: data.available ?? false,
      checkedAt: Date.now()
    };
    
    return ttsAvailabilityCache.available;
  } catch {
    ttsAvailabilityCache = {
      available: false,
      checkedAt: Date.now()
    };
    return false;
  }
}

export async function textToSpeech(
  text: string,
  voice?: string
): Promise<Blob> {
  // Check availability first
  const isAvailable = await checkTTSAvailability();
  
  if (!isAvailable) {
    throw new Error('TTS service is currently unavailable. Please try again later or check your network settings.');
  }

  try {
    const response = await fetch(`${API_BASE_URL}/api/tts/text-to-voice`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, voice }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'TTS generation failed');
    }

    return await response.blob();
  } catch (error) {
    // Clear cache on error so we check again next time
    ttsAvailabilityCache = null;
    throw error;
  }
}
```

#### Option C: Component-Level Check (Best UX)

```typescript
// AINose.tsx
import { useTTSAvailability } from '@/hooks/useTTSAvailability';

function AINose() {
  const { isAvailable, isChecking, healthStatus } = useTTSAvailability();
  const [showTTSWarning, setShowTTSWarning] = useState(false);

  const handleSpeak = async (text: string) => {
    // Don't try if TTS is unavailable
    if (!isAvailable) {
      setShowTTSWarning(true);
      setTimeout(() => setShowTTSWarning(false), 5000); // Hide after 5 seconds
      return;
    }

    try {
      const audioBlob = await textToSpeech(text);
      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);
      
      audio.onended = () => URL.revokeObjectURL(audioUrl);
      audio.onerror = () => {
        URL.revokeObjectURL(audioUrl);
        setShowTTSWarning(true);
      };
      
      await audio.play();
    } catch (error) {
      console.error('TTS error:', error);
      setShowTTSWarning(true);
    }
  };

  return (
    <div>
      {/* TTS Unavailable Warning */}
      {showTTSWarning && !isAvailable && (
        <div className="tts-warning" style={{
          padding: '12px',
          backgroundColor: '#fff3cd',
          border: '1px solid #ffc107',
          borderRadius: '4px',
          marginBottom: '16px',
          fontSize: '14px'
        }}>
          <strong>⚠️ Text-to-Speech Unavailable</strong>
          <p style={{ margin: '8px 0 0 0' }}>
            {healthStatus?.reason || 'TTS service is currently unavailable'}
          </p>
          {healthStatus?.suggestion && (
            <p style={{ margin: '4px 0 0 0', fontSize: '12px', color: '#666' }}>
              {healthStatus.suggestion}
            </p>
          )}
        </div>
      )}

      {/* Your component content */}
      
      {/* Disable TTS button if unavailable */}
      <button
        onClick={() => handleSpeak(text)}
        disabled={!isAvailable}
        title={!isAvailable ? 'TTS is currently unavailable' : 'Speak text'}
      >
        🔊 Speak
      </button>
    </div>
  );
}
```

### 3. Complete Example with Error Handling

```typescript
// api.ts - Complete implementation
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface TTSHealthResponse {
  status: string;
  available: boolean;
  reason?: string;
  can_generate_audio?: boolean;
  suggestion?: string;
}

let ttsHealthCache: { data: TTSHealthResponse; timestamp: number } | null = null;
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

export async function checkTTSHealth(): Promise<TTSHealthResponse> {
  // Check cache
  if (ttsHealthCache) {
    const age = Date.now() - ttsHealthCache.timestamp;
    if (age < CACHE_DURATION) {
      return ttsHealthCache.data;
    }
  }

  try {
    const response = await fetch(`${API_BASE_URL}/api/tts/health`);
    const data: TTSHealthResponse = await response.json();
    
    ttsHealthCache = {
      data,
      timestamp: Date.now()
    };
    
    return data;
  } catch (error) {
    // Return unavailable status on error
    const errorStatus: TTSHealthResponse = {
      status: 'unavailable',
      available: false,
      reason: 'Failed to check TTS health'
    };
    
    ttsHealthCache = {
      data: errorStatus,
      timestamp: Date.now()
    };
    
    return errorStatus;
  }
}

export async function textToSpeech(
  text: string,
  voice?: string
): Promise<Blob> {
  // Check health first
  const health = await checkTTSHealth();
  
  if (!health.available) {
    throw new Error(
      health.reason || 
      'TTS service is currently unavailable. Please try again later.'
    );
  }

  try {
    const response = await fetch(`${API_BASE_URL}/api/tts/text-to-voice`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text,
        voice: voice || 'ar-SA-HamedNeural',
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      // Clear cache on error
      ttsHealthCache = null;
      throw new Error(errorData.detail || 'TTS generation failed');
    }

    return await response.blob();
  } catch (error) {
    // Clear cache on error
    ttsHealthCache = null;
    throw error;
  }
}
```

### 4. Usage in Component

```typescript
// AINose.tsx
import { useState, useEffect } from 'react';
import { checkTTSHealth, textToSpeech } from '@/api/api';

function AINose() {
  const [ttsAvailable, setTtsAvailable] = useState<boolean | null>(null);
  const [ttsMessage, setTtsMessage] = useState<string>('');

  useEffect(() => {
    // Check TTS availability on mount
    checkTTSHealth().then(health => {
      setTtsAvailable(health.available);
      if (!health.available && health.reason) {
        setTtsMessage(health.reason);
      }
    });
  }, []);

  const handleSpeak = async (text: string) => {
    if (ttsAvailable === false) {
      alert('Text-to-speech is currently unavailable. ' + ttsMessage);
      return;
    }

    try {
      const audioBlob = await textToSpeech(text);
      // ... play audio
    } catch (error) {
      // Update availability on error
      const health = await checkTTSHealth();
      setTtsAvailable(health.available);
      setTtsMessage(health.reason || 'TTS failed');
      
      alert('فشل في توليد الصوت. ' + (health.reason || ''));
    }
  };

  return (
    <div>
      {ttsAvailable === false && (
        <div className="info-banner">
          ℹ️ Text-to-speech is unavailable: {ttsMessage}
        </div>
      )}
      
      <button 
        onClick={() => handleSpeak(text)}
        disabled={ttsAvailable === false}
      >
        🔊 Speak
      </button>
    </div>
  );
}
```

## Benefits

1. ✅ **No error spam**: Users don't see repeated 500 errors
2. ✅ **Better UX**: Clear messaging about TTS availability
3. ✅ **Performance**: Health check is cached to avoid repeated calls
4. ✅ **Graceful degradation**: App works fine without TTS
5. ✅ **Automatic recovery**: Re-checks when TTS becomes available

## Testing

```bash
# Test health endpoint
curl http://localhost:8000/api/tts/health | jq

# Should return availability status
```

## Summary

1. ✅ Backend health check endpoint added
2. ✅ Frontend can check TTS availability before using it
3. ✅ Graceful error handling without showing 500 errors
4. ✅ Better user experience with clear messaging

