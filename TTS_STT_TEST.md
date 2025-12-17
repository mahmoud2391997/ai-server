# TTS and STT Testing Guide

## ✅ Text-to-Speech (TTS) - WORKING

### Endpoint
```
POST /api/tts/synthesize
```

### Test Results
- ✅ Arabic TTS: Working
- ✅ English TTS: Working
- ✅ Multiple voices supported
- ✅ Fallback to ElevenLabs if Edge-TTS fails

### Test Command
```bash
# Arabic
curl -X POST http://localhost:8000/api/tts/synthesize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "مرحباً بك في أورا",
    "voice": "ar-SA-HamedNeural"
  }' \
  --output test_arabic.mp3

# English
curl -X POST http://localhost:8000/api/tts/synthesize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Welcome to Aura AI Server",
    "voice": "en-US-AriaNeural"
  }' \
  --output test_english.mp3
```

### Available Voices
- Arabic: `ar-SA-HamedNeural`, `ar-EG-SalmaNeural`
- English: `en-US-AriaNeural`, `en-US-JennyNeural`, `en-US-GuyNeural`, `en-GB-SoniaNeural`, `en-AU-NatashaNeural`

---

## 🔄 Speech-to-Text (STT) - READY (Server Restart Required)

### Endpoints
1. **File Upload**: `POST /api/tts/transcribe`
2. **Base64**: `POST /api/tts/transcribe-base64`

### Libraries Installed
- ✅ `SpeechRecognition` - For Google Web Speech API
- ✅ `openai-whisper` - For high-quality transcription

### Test Commands

#### Method 1: File Upload
```bash
curl -X POST http://localhost:8000/api/tts/transcribe \
  -F "language=ar" \
  -F "audio_file=@test_arabic.mp3"
```

#### Method 2: Base64 JSON
```bash
# Encode audio to base64
AUDIO_B64=$(base64 -i test_arabic.mp3 | tr -d '\n')

curl -X POST http://localhost:8000/api/tts/transcribe-base64 \
  -H "Content-Type: application/json" \
  -d "{
    \"audio_data\": \"$AUDIO_B64\",
    \"language\": \"ar\"
  }"
```

### Expected Response
```json
{
  "text": "مرحباً بك في أورا",
  "confidence": 0.95,
  "language": "ar"
}
```

### Supported Languages
- Arabic: `ar`
- English: `en`
- Auto-detect: `auto` (Whisper only)

### How It Works
1. **First tries Whisper** (best quality, offline)
2. **Falls back to Google Web Speech API** (via speech_recognition)
3. **Returns error if both fail**

---

## 🔄 Full Round-Trip Test

### Test: Text → Speech → Text
```bash
# 1. Generate speech from text
curl -X POST http://localhost:8000/api/tts/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text": "مرحباً، هذا اختبار", "voice": "ar-SA-HamedNeural"}' \
  --output roundtrip.mp3

# 2. Convert speech back to text
curl -X POST http://localhost:8000/api/tts/transcribe \
  -F "language=ar" \
  -F "audio_file=@roundtrip.mp3"
```

---

## ⚠️ Important Notes

1. **Server Restart Required**: After installing new libraries, restart the server:
   ```bash
   # Stop current server (Ctrl+C)
   python3 run.py
   ```

2. **Whisper Model Download**: On first use, Whisper will download the "base" model (~150MB). This happens automatically.

3. **Google Web Speech API**: Requires internet connection. Free but has rate limits.

4. **Audio Format**: Supports WAV, MP3, FLAC, and other common formats.

---

## 📊 Status Summary

| Feature | Status | Endpoint | Notes |
|---------|--------|----------|-------|
| Text-to-Speech | ✅ Working | `/api/tts/synthesize` | Tested and verified |
| Speech-to-Text | 🔄 Ready | `/api/tts/transcribe` | Libraries installed, needs server restart |
| Multiple Languages | ✅ Supported | Both endpoints | Arabic, English, and more |
| Fallback Systems | ✅ Implemented | Both endpoints | Multiple providers |

---

## 🐛 Troubleshooting

### STT returns "service unavailable"
- **Solution**: Restart the server to load new libraries
- **Check**: Verify libraries are installed: `pip list | grep -E "whisper|SpeechRecognition"`

### Whisper slow on first use
- **Normal**: First use downloads the model (~150MB)
- **Solution**: Model is cached after first download

### Google Speech API errors
- **Check**: Internet connection required
- **Fallback**: Whisper works offline

### Audio format not supported
- **Supported**: WAV, MP3, FLAC, OGG
- **Solution**: Convert audio to WAV if needed

