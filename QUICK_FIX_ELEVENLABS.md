# 🚀 Quick Fix: ElevenLabs Podcast Generation

## Problem
❌ Error: "The API key you used is missing the permission text_to_speech"

## Solution (5 minutes)

### 1. Go to ElevenLabs
🔗 https://elevenlabs.io → Profile → Developers → API Keys

### 2. Create New Key
Click **"Create Key"** and enable:
- ✅ **Text to Speech**
- ✅ **Read access for Voices**

### 3. Copy Key
Copy the new API key to clipboard

### 4. Update .env File
Open `.env` in your project and replace:
```
ELEVENLABS_API_KEY=your_new_key_here
```

### 5. Restart App
Stop and start the Wireless Monitor application

### 6. Test
Go to http://127.0.0.1:8080/weekly_digest and click **"🎙️ Generate Podcast"**

## ✅ Done!
Your podcast should now generate successfully.

---

## What's Working Now
✅ Export script as `.txt` file
✅ Script formatting with breaks
✅ Error messages with guidance
⚠️ Podcast generation (after API key fix)

## Need Help?
See `ELEVENLABS_API_KEY_PERMISSIONS_FIX.md` for detailed instructions.
