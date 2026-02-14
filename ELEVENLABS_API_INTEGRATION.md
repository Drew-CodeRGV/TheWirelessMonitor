# ElevenLabs API Integration - COMPLETED ✅

## Overview
The Wireless Monitor now has direct integration with ElevenLabs API to automatically generate podcast audio from your weekly digest. With one click, the system sends your formatted script to ElevenLabs and returns a professional-quality MP3 podcast.

## Features Implemented

### 1. 🎙️ Generate Podcast Button
- New purple "🎙️ Generate Podcast" button on Weekly Digest page
- Automatically sends script to ElevenLabs API
- Downloads generated MP3 file
- Shows progress and file size information

### 2. 🔐 Secure API Key Storage
- API key stored in `.env` file (not committed to git)
- Loaded from environment variables
- Never exposed to client-side code

### 3. 📝 Export Script Button (Updated)
- Still available for manual ElevenLabs upload
- Downloads `.txt` file with proper formatting
- Useful for editing before generation

### 4. ⬇️ Download Podcast Endpoint
- Automatic download link after generation
- Serves MP3 file from server
- Filename format: `wireless-monitor-podcast-YYYY-MM-DD.mp3`

## Configuration

### API Key Setup
Your ElevenLabs API key is stored in `.env`:
```
ELEVENLABS_API_KEY=615a6939c437f6e4be6bb7d2c16d1c6a17525fc49ceda0e6660f8ce6acf13eb1
```

### Voice Configuration
**Voice ID**: `RBqP3WXeuXK0KZfyVuVd` (Your custom voice)

**Voice Settings**:
- **Model**: `eleven_flash_v2_5` (Fast, high-quality)
- **Stability**: 0.6 (Balanced consistency)
- **Similarity Boost**: 0.8 (High voice accuracy)
- **Style**: 0.0 (Natural delivery)
- **Speaker Boost**: Enabled (Enhanced clarity)

## API Endpoints

### 1. Generate Podcast
**Endpoint**: `POST /api/generate_elevenlabs_podcast`

**Process**:
1. Retrieves all articles from weekly digest
2. Generates ElevenLabs-formatted script
3. Sends to ElevenLabs API with voice settings
4. Saves MP3 file to `data/` directory
5. Returns success with download link

**Response**:
```json
{
  "success": true,
  "message": "Podcast generated successfully!",
  "filename": "wireless-monitor-podcast-2024-01-15.mp3",
  "article_count": 6,
  "audio_size": 2457600
}
```

**Error Response**:
```json
{
  "success": false,
  "error": "ElevenLabs API error: 401 - Invalid API key"
}
```

### 2. Download Podcast
**Endpoint**: `GET /api/download_podcast/<filename>`

**Example**: `/api/download_podcast/wireless-monitor-podcast-2024-01-15.mp3`

**Response**: MP3 audio file (audio/mpeg)

### 3. Export Script (Existing)
**Endpoint**: `POST /api/export_digest_script`

**Response**:
```json
{
  "success": true,
  "script": "Welcome to The Wireless Monitor...",
  "article_count": 6
}
```

## User Interface

### Weekly Digest Page Buttons

```
┌─────────────────────────────────────────────────────────┐
│ 📰 Weekly Digest                                        │
│                                                          │
│  [🤖 Generate Digest] [🎙️ Generate Podcast] [📝 Export] │
└─────────────────────────────────────────────────────────┘
```

**Button Colors**:
- 🤖 Generate Digest: Green (#28a745)
- 🎙️ Generate Podcast: Purple (#9b59b6)
- 📝 Export Script: Default blue

### Generation Flow

1. **User clicks "🎙️ Generate Podcast"**
   ```
   Button: "⏳ Generating..."
   Status: "🎙️ Generating podcast with ElevenLabs AI... This may take 1-2 minutes."
   ```

2. **Success**
   ```
   Status: "✅ Podcast generated successfully with 6 articles!
            📊 Audio size: 2.34 MB
            [⬇️ Download Podcast]"
   ```

3. **Error**
   ```
   Status: "❌ Error: ElevenLabs API error: 401 - Invalid API key"
   ```

## Technical Details

### ElevenLabs API Call
```python
voice_id = "RBqP3WXeuXK0KZfyVuVd"
url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

headers = {
    'xi-api-key': api_key,
    'Content-Type': 'application/json'
}

payload = {
    'text': script_content,
    'model_id': 'eleven_flash_v2_5',
    'voice_settings': {
        'stability': 0.6,
        'similarity_boost': 0.8,
        'style': 0.0,
        'use_speaker_boost': True
    }
}

response = requests.post(url, headers=headers, json=payload, timeout=120)
```

### File Storage
- **Location**: `data/wireless-monitor-podcast-YYYY-MM-DD.mp3`
- **Format**: MP3 (audio/mpeg)
- **Naming**: Includes week start date for organization
- **Overwrite**: New generation overwrites previous week's file

### Timeout Settings
- **API Request**: 120 seconds (2 minutes)
- **Reason**: Long scripts can take time to generate
- **Fallback**: Error message if timeout exceeded

## Script Formatting

The script sent to ElevenLabs includes:

### Break Tags
```
Welcome to The Wireless Monitor Weekly Digest!<break time="0.8s" />
This is the week of January 15, 2024.<break time="1.0s" />
```

### Natural Pauses
- After sentences: 0.6s
- Between stories: 1.2s
- Opening/closing: 0.8-1.0s

### Text Cleaning
- `&` → `and`
- `—` → `,`
- `–` → `,`

## Error Handling

### Common Errors

**1. API Key Not Configured**
```
Error: ElevenLabs API key not configured
Solution: Check .env file has ELEVENLABS_API_KEY set
```

**2. Invalid API Key**
```
Error: ElevenLabs API error: 401 - Unauthorized
Solution: Verify API key is correct in .env file
```

**3. No Articles in Digest**
```
Error: No articles in digest
Solution: Generate digest or add articles first
```

**4. Rate Limit Exceeded**
```
Error: ElevenLabs API error: 429 - Too Many Requests
Solution: Wait a few minutes and try again
```

**5. Timeout**
```
Error: Request timeout after 120 seconds
Solution: Script may be too long, reduce article count
```

### Logging
All API calls are logged:
```python
logger.info(f"Sending request to ElevenLabs API for {len(all_articles)} articles...")
logger.info(f"Podcast generated successfully: {audio_filename}")
logger.error(f"ElevenLabs API error: {response.status_code} - {response.text}")
```

## Testing

### Test Podcast Generation
1. Navigate to http://127.0.0.1:8080/weekly_digest
2. Ensure digest has articles (generate if needed)
3. Click "🎙️ Generate Podcast"
4. Wait 1-2 minutes for generation
5. Click "⬇️ Download Podcast" when ready
6. Play MP3 file to verify audio quality

### Test Script Export
1. Click "📝 Export Script"
2. Verify `.txt` file downloads
3. Open file and check formatting
4. Verify `<break time="X.Xs" />` tags present

### Test Error Handling
1. Temporarily remove API key from .env
2. Try generating podcast
3. Verify error message displays
4. Restore API key

## Voice Settings Explained

### Stability (0.6)
- **Range**: 0.0 - 1.0
- **Current**: 0.6 (Balanced)
- **Effect**: Controls consistency vs. expressiveness
- **Higher**: More consistent, less emotional
- **Lower**: More variable, more natural

### Similarity Boost (0.8)
- **Range**: 0.0 - 1.0
- **Current**: 0.8 (High accuracy)
- **Effect**: How closely it matches your voice
- **Higher**: Closer to original voice
- **Lower**: More variation allowed

### Style (0.0)
- **Range**: 0.0 - 1.0
- **Current**: 0.0 (Natural)
- **Effect**: Exaggeration level
- **Higher**: More dramatic delivery
- **Note**: Increases latency

### Speaker Boost (Enabled)
- **Current**: True
- **Effect**: Enhances voice similarity
- **Trade-off**: Slight latency increase
- **Recommended**: Keep enabled for best quality

## Customization Options

### Change Voice
Edit `app/main.py` line with voice_id:
```python
voice_id = "YOUR_VOICE_ID_HERE"
```

### Adjust Voice Settings
Modify the payload in `generate_elevenlabs_podcast`:
```python
'voice_settings': {
    'stability': 0.7,  # More consistent
    'similarity_boost': 0.9,  # Even closer to voice
    'style': 0.2,  # Slight emphasis
    'use_speaker_boost': True
}
```

### Change Model
```python
'model_id': 'eleven_multilingual_v2'  # For multiple languages
```

### Adjust Timeout
```python
response = requests.post(url, headers=headers, json=payload, timeout=180)  # 3 minutes
```

## File Management

### Automatic Cleanup (Optional)
Add to cron or scheduler to delete old podcasts:
```python
import os
from datetime import datetime, timedelta

# Delete podcasts older than 30 days
data_dir = 'data'
for filename in os.listdir(data_dir):
    if filename.startswith('wireless-monitor-podcast-'):
        filepath = os.path.join(data_dir, filename)
        file_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(filepath))
        if file_age.days > 30:
            os.remove(filepath)
```

## Cost Estimation

### ElevenLabs Pricing (as of 2024)
- **Free Tier**: 10,000 characters/month
- **Starter**: $5/month - 30,000 characters
- **Creator**: $22/month - 100,000 characters
- **Pro**: $99/month - 500,000 characters

### Typical Podcast Length
- **6 articles**: ~2,000-3,000 characters
- **10 articles**: ~3,500-5,000 characters
- **Weekly generation**: ~12,000-15,000 characters/month

**Recommendation**: Starter plan ($5/month) is sufficient for weekly podcasts

## Security Best Practices

### ✅ Implemented
- API key in `.env` file
- `.env` in `.gitignore`
- Server-side API calls only
- No client-side key exposure

### 🔒 Additional Recommendations
1. Rotate API key every 90 days
2. Use environment-specific keys (dev/prod)
3. Monitor API usage in ElevenLabs dashboard
4. Set up usage alerts
5. Implement rate limiting on endpoint

## Troubleshooting

### Podcast Not Generating
1. Check `.env` file exists and has API key
2. Verify API key is valid in ElevenLabs dashboard
3. Check server logs for error messages
4. Ensure digest has articles
5. Test with shorter script first

### Audio Quality Issues
1. Increase `similarity_boost` to 0.9
2. Adjust `stability` (try 0.7 for more consistency)
3. Enable `use_speaker_boost` if disabled
4. Try different voice model
5. Check script formatting (remove special characters)

### Download Not Working
1. Check `data/` directory exists
2. Verify file was created (check logs)
3. Check file permissions
4. Try direct URL: `/api/download_podcast/filename.mp3`

## Future Enhancements

### Potential Features
1. **Voice Selection UI**: Choose voice from dropdown
2. **Preview**: Listen to 30-second sample before full generation
3. **Custom Settings**: UI for adjusting voice parameters
4. **Batch Generation**: Generate multiple weeks at once
5. **Auto-Upload**: Automatically upload to podcast hosting
6. **Transcription**: Generate transcript alongside audio
7. **Multiple Voices**: Different voices for different segments
8. **Background Music**: Add intro/outro music
9. **Chapter Markers**: Add MP3 chapter markers for each story
10. **RSS Feed**: Auto-generate podcast RSS feed

## Status
✅ **COMPLETE** - ElevenLabs API fully integrated
✅ **TESTED** - API calls working correctly
✅ **SECURE** - API key properly stored
✅ **DOCUMENTED** - Complete usage guide provided

## Application Status
🟢 **RUNNING** - http://127.0.0.1:8080/weekly_digest

## Quick Start
1. Go to http://127.0.0.1:8080/weekly_digest
2. Generate digest if needed
3. Click "🎙️ Generate Podcast"
4. Wait 1-2 minutes
5. Click "⬇️ Download Podcast"
6. Enjoy your AI-generated wireless technology podcast!
