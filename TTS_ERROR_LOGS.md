# TTS Endpoint Error Logs

## Error Summary

**Status**: 500 Internal Server Error  
**Error Type**: `edge_tts.exceptions.NoAudioReceived`  
**Error Message**: "No audio was received. Please verify that your parameters are correct."

## Detailed Log Output

```
TTS ERROR: NoAudioReceived
============================================================
Error message: No audio was received. Please verify that your parameters are correct.
Text: test...
Voice: ar-SA-HamedNeural
Rate: +0%, Pitch: +0Hz, Volume: +0%

This error occurs when:
1. Edge TTS service is reachable (can get metadata)
2. But the audio streaming connection is blocked

Common causes:
- Proxy/firewall blocking WebSocket or streaming connections
- Network restrictions on specific Edge TTS endpoints
- Corporate firewall blocking audio streaming

Current environment:
  NO_PROXY: *
  HTTP_PROXY: Not set
  HTTPS_PROXY: Not set
============================================================
```

## Full Stack Trace

```
Error in communicate.save(): NoAudioReceived: No audio was received. Please verify that your parameters are correct.
Traceback (most recent call last):
  File "/Users/mahmoudelsayed/Documents/GitHub/aura-ai/ai-server/app/routers/tts.py", line 104, in synthesize_speech
    await communicate.save(temp_path)
  File "/Users/mahmoudelsayed/Downloads/ai-server/venv/lib/python3.14/site-packages/edge_tts/communicate.py", line 590, in save
    async for message in self.stream():
  File "/Users/mahmoudelsayed/Downloads/ai-server/venv/lib/python3.14/site-packages/edge_tts/communicate.py", line 566, in stream
    async for message in self.__stream():
        yield message
  File "/Users/mahmoudelsayed/Downloads/ai-server/venv/lib/python3.14/site-packages/edge_tts/communicate.py", line 541, in __stream
    raise NoAudioReceived(
        "No audio was received. Please verify that your parameters are correct."
    )
edge_tts.exceptions.NoAudioReceived: No audio was received. Please verify that your parameters are correct.
```

## Root Cause Analysis

1. **Connection Status**: Edge TTS service is reachable
   - Can successfully list voices
   - Can create `Communicate` object
   - Can establish initial connection

2. **Streaming Failure**: Audio streaming connection is blocked
   - The `stream()` method fails to receive audio data
   - This happens in `edge_tts/communicate.py` at line 541
   - The library connects but doesn't receive the audio stream

3. **Environment Configuration**: Proxy settings are correctly disabled
   - `NO_PROXY: *` is set
   - `HTTP_PROXY` and `HTTPS_PROXY` are unset
   - But the issue persists

## Why This Happens

The Edge TTS service uses a two-step process:
1. **Metadata Connection**: HTTP request to get SSML and voice info (✅ Works)
2. **Audio Streaming**: WebSocket or streaming connection to receive audio (❌ Blocked)

Even though HTTP_PROXY is disabled, the streaming connection might be:
- Using a different protocol (WebSocket)
- Going through a system-level proxy
- Blocked by firewall rules
- Restricted by network policies

## Solutions

### Option 1: Check System Proxy Settings
```bash
# Check if system proxy is set
echo $HTTP_PROXY
echo $HTTPS_PROXY
echo $ALL_PROXY

# Check macOS proxy settings
networksetup -getwebproxy "Wi-Fi"
networksetup -getsecurewebproxy "Wi-Fi"
```

### Option 2: Use Alternative TTS Service
Consider using a different TTS service that doesn't rely on streaming:
- Google Cloud Text-to-Speech
- AWS Polly
- Azure Cognitive Services
- OpenAI TTS API

### Option 3: Test from Different Network
Test if the issue is network-specific:
- Try from a different network (mobile hotspot, different WiFi)
- Test from a server without proxy restrictions

### Option 4: Configure Proxy to Allow Edge TTS
If you must use a proxy, configure it to allow:
- `speech.platform.bing.com` (Edge TTS endpoint)
- WebSocket connections
- Streaming connections on port 443

## Current Server Logs Location

Server logs are being written to: `server.log` in the project root.

To view real-time logs:
```bash
tail -f server.log
```

## Testing the Endpoint

```bash
# Test TTS endpoint
curl -X POST "http://localhost:8000/api/tts/text-to-voice" \
  -H "Content-Type: application/json" \
  -d '{"text": "مرحبا"}' \
  -o output.mp3

# Check response
echo "Status: $?"
file output.mp3
```

## Next Steps

1. ✅ Enhanced logging implemented
2. ✅ Error details captured
3. ⏳ Investigate system-level proxy settings
4. ⏳ Consider alternative TTS solutions if proxy cannot be configured
5. ⏳ Test from different network environment

