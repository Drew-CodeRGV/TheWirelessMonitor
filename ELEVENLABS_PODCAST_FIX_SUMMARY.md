# ElevenLabs Podcast Generation - Fix Summary

## Issue Resolved
Fixed the sqlite3.Row to dictionary conversion error that was preventing the podcast script from being generated.

## Issues Identified and Fixed

### 1. ✅ FIXED: sqlite3.Row AttributeError
**Problem**: `'sqlite3.Row' object has no attribute 'get'`

**Root Cause**: The `fetchall()` method returns `sqlite3.Row` objects, but the `generate_podcast_script()` function expects dictionaries with `.get()` method support.

**Solution**: Convert Row objects to dictionaries before passing to the script generator:
```python
# Convert Row objects to dictionaries
all_articles = [dict(row) for row in all_articles_rows]
```

**Files Modified**:
- `app/main.py` (line ~2007): `/api/generate_elevenlabs_podcast` endpoint
- `app/main.py` (line ~1960): `/api/export_digest_script` endpoint

### 2. ⚠️ REQUIRES USER ACTION: API Key Permissions
**Problem**: ElevenLabs API returns 401 error:
```
"The API key you used is missing the permission text_to_speech to execute this operation."
```

**Root Cause**: The API key was created without the required `text_to_speech` permission enabled.

**Solution**: User must regenerate the API key with correct permissions.

**Enhanced Error Message**: Added helpful error message that guides users to the fix:
```
"API Key Permission Error: Your ElevenLabs API key is missing the 'text_to_speech' permission. 
Please regenerate your API key at elevenlabs.io with 'Text to Speech' and 'Read access for Voices' enabled. 
See ELEVENLABS_API_KEY_PERMISSIONS_FIX.md for detailed instructions."
```

## User Action Required

### Step-by-Step: Regenerate ElevenLabs API Key

1. **Go to ElevenLabs Dashboard**
   - Visit [elevenlabs.io](https://elevenlabs.io)
   - Log in to your account
   - Navigate to: Profile → Developers → API Keys

2. **Create New API Key**
   - Click **"Create Key"**
   - **Enable these permissions**:
     - ✅ Text to Speech
     - ✅ Read access for Voices
   - Optional: Set a name ("Wireless Monitor") and credit limit

3. **Update .env File**
   - Copy the new API key
   - Open `.env` file in your project
   - Replace the value:
     ```
     ELEVENLABS_API_KEY=your_new_api_key_here
     ```
   - Save the file

4. **Restart Application**
   - The app will automatically load the new key
   - Try generating the podcast again

## Testing the Fix

### Test 1: Export Script (Should Work Now)
1. Go to Weekly Digest page
2. Click **"📝 Export Script"** button
3. ✅ Should download a `.txt` file with the podcast script

### Test 2: Generate Podcast (Requires New API Key)
1. Go to Weekly Digest page
2. Click **"🎙️ Generate Podcast"** button
3. ⚠️ Will show permission error until API key is regenerated
4. After regenerating key: ✅ Should generate MP3 file

## Technical Details

### ElevenLabs API Configuration
- **Endpoint**: `https://api.elevenlabs.io/v1/text-to-speech/{voice_id}`
- **Voice ID**: `RBqP3WXeuXK0KZfyVuVd` (user's custom voice)
- **Model**: `eleven_flash_v2_5` (fast, high-quality)
- **Voice Settings**:
  - Stability: 0.6
  - Similarity Boost: 0.8
  - Style: 0.0
  - Speaker Boost: Enabled

### Script Formatting
The podcast script includes ElevenLabs-compatible break tags:
- `<break time="0.4s" />` - Short pause
- `<break time="0.6s" />` - Sentence pause
- `<break time="1.0s" />` - Story transition
- `<break time="1.5s" />` - Section break

### File Output
- **Location**: `data/wireless-monitor-podcast-{week_start}.mp3`
- **Format**: MP3 audio file
- **Download**: Available via `/api/download_podcast/{filename}` endpoint

## Files Created/Modified

### New Files
1. `ELEVENLABS_API_KEY_PERMISSIONS_FIX.md` - Detailed guide for regenerating API key
2. `ELEVENLABS_PODCAST_FIX_SUMMARY.md` - This summary document

### Modified Files
1. `app/main.py`:
   - Fixed Row to dict conversion in `/api/generate_elevenlabs_podcast`
   - Fixed Row to dict conversion in `/api/export_digest_script`
   - Enhanced error handling with helpful permission error message

## Current Status

✅ **Working**:
- Export podcast script as `.txt` file
- Script formatting with ElevenLabs break tags
- Digest article selection and ordering
- Error handling with helpful messages

⚠️ **Requires User Action**:
- Regenerate ElevenLabs API key with correct permissions
- Update `.env` file with new key
- Restart application

🎯 **Next Steps**:
1. User regenerates API key with permissions
2. User updates `.env` file
3. User restarts app
4. User tests podcast generation
5. ✅ Feature complete!

## Support Resources
- [ElevenLabs API Documentation](https://elevenlabs.io/docs)
- [API Key Management](https://elevenlabs.io/docs/api-reference/authentication)
- Project Documentation: `ELEVENLABS_API_KEY_PERMISSIONS_FIX.md`
