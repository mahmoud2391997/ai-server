# Frontend TTS Error Handling Fix

## Problem
The frontend is receiving a 500 error from the TTS endpoint but not handling it gracefully. The error shows:
- `POST http://localhost:8000/api/tts/text-to-voice 500 (Internal Server Error)`
- Error caught at `api.ts:340` and `api.ts:420`
- Called from `AINose.tsx:271` in `handleSpeak`

## Backend Error Response Format

When the TTS endpoint fails, it returns:
```json
{
  "detail": "TTS service could not generate audio. The Edge TTS service is reachable but audio streaming is blocked. This is often caused by proxy or firewall settings. Please check your network configuration or contact your system administrator."
}
```

## Frontend Fix

### 1. Update `api.ts` - TTS Function (around line 340)

```typescript
// api.ts
export async function textToSpeech(
  text: string,
  voice?: string
): Promise<Blob> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/tts/text-to-voice`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text,
        voice: voice || 'ar-SA-HamedNeural',
      }),
    });

    // Check if response is OK
    if (!response.ok) {
      // Try to parse error response
      let errorMessage = 'TTS generation failed';
      
      try {
        const errorData = await response.json();
        errorMessage = errorData.detail || errorMessage;
      } catch (e) {
        // If JSON parsing fails, use status text
        errorMessage = response.statusText || errorMessage;
      }
      
      // Create a more user-friendly error
      const friendlyError = new Error(errorMessage);
      // Add status code for debugging
      (friendlyError as any).status = response.status;
      throw friendlyError;
    }

    // Return audio blob
    return await response.blob();
  } catch (error) {
    // Re-throw with better context
    if (error instanceof Error) {
      throw error;
    }
    throw new Error('TTS generation failed: Unknown error');
  }
}
```

### 2. Update `AINose.tsx` - handleSpeak Function (around line 271)

```typescript
// AINose.tsx
const handleSpeak = async (text: string) => {
  if (!text || text.trim().length === 0) {
    console.warn('Empty text provided to TTS');
    return;
  }

  try {
    // Show loading state if you have one
    setIsSpeaking?.(true);
    
    const audioBlob = await textToSpeech(text);
    
    // Create audio URL and play
    const audioUrl = URL.createObjectURL(audioBlob);
    const audio = new Audio(audioUrl);
    
    // Handle audio playback
    audio.onended = () => {
      URL.revokeObjectURL(audioUrl);
      setIsSpeaking?.(false);
    };
    
    audio.onerror = (e) => {
      console.error('Audio playback error:', e);
      URL.revokeObjectURL(audioUrl);
      setIsSpeaking?.(false);
      // Show user-friendly error
      alert('فشل في تشغيل الصوت. يرجى المحاولة مرة أخرى.');
    };
    
    await audio.play();
    
  } catch (error) {
    console.error('TTS error:', error);
    setIsSpeaking?.(false);
    
    // Extract error message
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    
    // Show user-friendly error message
    // Option 1: Alert (simple)
    if (errorMessage.includes('proxy') || errorMessage.includes('network') || errorMessage.includes('firewall')) {
      alert('مشكلة في الاتصال بالشبكة. يرجى التحقق من إعدادات الشبكة أو المحاولة لاحقاً.');
    } else if (errorMessage.includes('empty') || errorMessage.includes('Text cannot be empty')) {
      alert('النص فارغ. يرجى إدخال نص للتحويل إلى صوت.');
    } else {
      alert('فشل في توليد الصوت. يرجى المحاولة مرة أخرى.');
    }
    
    // Option 2: Toast notification (better UX)
    // toast.error(getErrorMessage(errorMessage));
    
    // Option 3: Set error state for UI display
    // setTtsError(errorMessage);
  }
};
```

### 3. Better Error Handling with Error Types

Create a utility function for better error handling:

```typescript
// utils/ttsErrors.ts
export enum TTSErrorType {
  NETWORK = 'NETWORK',
  EMPTY_TEXT = 'EMPTY_TEXT',
  SERVICE_UNAVAILABLE = 'SERVICE_UNAVAILABLE',
  UNKNOWN = 'UNKNOWN',
}

export interface TTSError {
  type: TTSErrorType;
  message: string;
  originalError?: Error;
}

export function parseTTSError(error: unknown): TTSError {
  if (!(error instanceof Error)) {
    return {
      type: TTSErrorType.UNKNOWN,
      message: 'حدث خطأ غير معروف',
    };
  }

  const message = error.message.toLowerCase();
  
  if (message.includes('proxy') || message.includes('network') || message.includes('firewall')) {
    return {
      type: TTSErrorType.NETWORK,
      message: 'مشكلة في الاتصال بالشبكة. يرجى التحقق من إعدادات الشبكة.',
      originalError: error,
    };
  }
  
  if (message.includes('empty') || message.includes('text cannot be empty')) {
    return {
      type: TTSErrorType.EMPTY_TEXT,
      message: 'النص فارغ. يرجى إدخال نص للتحويل إلى صوت.',
      originalError: error,
    };
  }
  
  if (message.includes('service') || message.includes('unavailable') || message.includes('blocked')) {
    return {
      type: TTSErrorType.SERVICE_UNAVAILABLE,
      message: 'خدمة تحويل النص إلى صوت غير متاحة حالياً. يرجى المحاولة لاحقاً.',
      originalError: error,
    };
  }
  
  return {
    type: TTSErrorType.UNKNOWN,
    message: 'فشل في توليد الصوت. يرجى المحاولة مرة أخرى.',
    originalError: error,
  };
}

// Usage in handleSpeak
import { parseTTSError } from '@/utils/ttsErrors';

const handleSpeak = async (text: string) => {
  try {
    // ... TTS code ...
  } catch (error) {
    const ttsError = parseTTSError(error);
    
    // Show error based on type
    switch (ttsError.type) {
      case TTSErrorType.NETWORK:
        // Show network error UI
        break;
      case TTSErrorType.EMPTY_TEXT:
        // Show empty text warning
        break;
      case TTSErrorType.SERVICE_UNAVAILABLE:
        // Show service unavailable message
        break;
      default:
        // Show generic error
    }
    
    // Log for debugging
    console.error('TTS Error:', ttsError);
  }
};
```

### 4. Using Axios (if you're using Axios)

If your `api.ts` uses Axios:

```typescript
// api.ts
import axios from 'axios';

export async function textToSpeech(
  text: string,
  voice?: string
): Promise<Blob> {
  try {
    const response = await axios.post(
      `${API_BASE_URL}/api/tts/text-to-voice`,
      {
        text,
        voice: voice || 'ar-SA-HamedNeural',
      },
      {
        responseType: 'blob', // Important for binary data
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    return response.data;
  } catch (error) {
    // Axios error handling
    if (axios.isAxiosError(error)) {
      let errorMessage = 'TTS generation failed';
      
      if (error.response) {
        // Server responded with error status
        try {
          // Try to parse error response as JSON
          const text = await error.response.data.text();
          const errorData = JSON.parse(text);
          errorMessage = errorData.detail || errorMessage;
        } catch (e) {
          // If it's not JSON, use status text
          errorMessage = error.response.statusText || errorMessage;
        }
      } else if (error.request) {
        // Request was made but no response received
        errorMessage = 'No response from server. Please check your connection.';
      } else {
        // Something else happened
        errorMessage = error.message || errorMessage;
      }
      
      const friendlyError = new Error(errorMessage);
      (friendlyError as any).status = error.response?.status;
      throw friendlyError;
    }
    
    throw error;
  }
}
```

### 5. Complete Example with React Hook

```typescript
// hooks/useTextToSpeech.ts
import { useState, useCallback } from 'react';
import { textToSpeech } from '@/api/api';
import { parseTTSError, TTSErrorType } from '@/utils/ttsErrors';

export function useTextToSpeech() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [errorType, setErrorType] = useState<TTSErrorType | null>(null);

  const speak = useCallback(async (text: string, voice?: string) => {
    setIsLoading(true);
    setError(null);
    setErrorType(null);

    try {
      const audioBlob = await textToSpeech(text, voice);
      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);

      return new Promise<void>((resolve, reject) => {
        audio.onended = () => {
          URL.revokeObjectURL(audioUrl);
          setIsLoading(false);
          resolve();
        };

        audio.onerror = (e) => {
          URL.revokeObjectURL(audioUrl);
          setIsLoading(false);
          reject(new Error('Audio playback failed'));
        };

        audio.play().catch((e) => {
          URL.revokeObjectURL(audioUrl);
          setIsLoading(false);
          reject(e);
        });
      });
    } catch (err) {
      const ttsError = parseTTSError(err);
      setError(ttsError.message);
      setErrorType(ttsError.type);
      setIsLoading(false);
      throw ttsError;
    }
  }, []);

  return {
    speak,
    isLoading,
    error,
    errorType,
    clearError: () => {
      setError(null);
      setErrorType(null);
    },
  };
}

// Usage in component
function AINose() {
  const { speak, isLoading, error, errorType } = useTextToSpeech();

  const handleSpeak = async (text: string) => {
    try {
      await speak(text);
    } catch (error) {
      // Error is already handled by the hook
      // You can show toast/notification here if needed
      console.error('TTS failed:', error);
    }
  };

  return (
    <div>
      {/* Your component */}
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}
      {isLoading && <div>Generating audio...</div>}
    </div>
  );
}
```

## Quick Fix Summary

**In `api.ts` (around line 340):**
- Check `response.ok` before processing
- Parse error JSON response
- Throw meaningful error messages

**In `AINose.tsx` (around line 271):**
- Wrap `textToSpeech` call in try-catch
- Show user-friendly error messages
- Handle different error types appropriately

## Testing

After implementing the fix, test with:
1. Valid text → Should work
2. Empty text → Should show appropriate error
3. Network error → Should show network error message
4. Service unavailable → Should show service unavailable message

