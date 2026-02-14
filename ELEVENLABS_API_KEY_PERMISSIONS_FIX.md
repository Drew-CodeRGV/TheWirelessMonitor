# ElevenLabs API Key Permissions Fix

## Problem
The ElevenLabs API is returning a 401 error:
```
"The API key you used is missing the permission text_to_speech to execute this operation."
```

## Root Cause
The API key was created without the required `text_to_speech` permission enabled. ElevenLabs API keys require specific permissions to be explicitly enabled when creating the key.

## Solution: Regenerate API Key with Correct Permissions

### Step 1: Go to ElevenLabs Developer Settings
1. Log in to your ElevenLabs account at [elevenlabs.io](https://elevenlabs.io)
2. Click on your profile icon in the bottom-left corner
3. Navigate to **Developers** section → **API Keys**

### Step 2: Create New API Key with Permissions
1. Click **"Create Key"** button
2. **IMPORTANT**: Enable the following permissions:
   - ✅ **Text to Speech** (required for podcast generation)
   - ✅ **Read access for Voices** (required to use your custom voice)
3. Optional settings:
   - Give it a name (e.g., "Wireless Monitor Podcast")
   - Set a monthly credit usage limit (recommended to prevent unexpected charges)

### Step 3: Copy and Update API Key
1. Click **"Create Key"** and copy the newly generated API key
2. Open the `.env` file in your Wireless Monitor project
3. Replace the existing `ELEVENLABS_API_KEY` value with the new key:
   ```
   ELEVENLABS_API_KEY=your_new_api_key_here
   ```
4. Save the file

### Step 4: Restart the Application
1. Stop the running Wireless Monitor application
2. Start it again to load the new API key
3. Try generating the podcast again

## Verification
After updating the API key:
1. Go to the Weekly Digest page
2. Click the purple **"🎙️ Generate Podcast"** button
3. The podcast should now generate successfully without the 401 error

## Important Notes
- **Keep your API key secure**: Never commit the `.env` file to version control
- **Monitor your credits**: ElevenLabs charges based on character usage
- **Voice ID**: Your custom voice ID `RBqP3WXeuXK0KZfyVuVd` is already configured in the code
- **Model**: Using `eleven_flash_v2_5` for fast, high-quality generation

## Alternative: Check Existing Key Permissions
If you want to check the permissions of your existing API key:
1. Go to ElevenLabs → Developers → API Keys
2. Look for your current key in the list
3. Check if "Text to Speech" permission is enabled
4. If not, you'll need to create a new key (permissions cannot be edited after creation)

## Reference
- [ElevenLabs API Documentation](https://elevenlabs.io/docs)
- [API Key Management Guide](https://elevenlabs.io/docs/api-reference/authentication)
