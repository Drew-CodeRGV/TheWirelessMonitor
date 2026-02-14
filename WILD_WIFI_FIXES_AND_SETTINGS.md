# Wild Wi-Fi Fixes and Settings Feature

## Issues Fixed

### 1. ✅ Stories Not Posting
**Problem**: Submitted stories were set to `approved = 0` (requiring manual approval) and never appeared on the page.

**Solution**: Changed `approved` to `1` in the submit endpoint so stories are auto-approved and appear immediately.

**File Modified**: `app/main.py` (line ~2478)

### 2. ✅ Refresh Endpoint Error
**Problem**: The refresh endpoint was calling `self.wild_wifi_curator.curate_stories()` which doesn't exist.

**Solution**: Updated to call the correct methods:
- `update_all_scores()` - Recalculates quality and humor scores
- `update_featured_stories()` - Updates featured story status

**File Modified**: `app/main.py` (line ~2527)

## New Feature: Wild Wi-Fi Settings Page

### Overview
Added a comprehensive settings page where you can configure the AI prompt for generating Wild Wi-Fi stories.

### Features

#### 1. Statistics Dashboard
- Total stories count
- Approved stories count
- Pending stories count (for future approval workflow)

#### 2. AI Prompt Configuration
- **Edit Prompt**: Full-featured textarea to customize the AI generation prompt
- **Save Prompt**: Saves your custom prompt to the database
- **Reset to Default**: Restores the default prompt template
- **Test Generate**: Tests story generation with current prompt (placeholder for now)

#### 3. Default Prompt Template
Includes guidelines for:
- Story length (100-300 words)
- Tone (humorous, professional, ironic)
- Required elements (location, technical insight, category)
- Example themes
- Available categories

### How to Access

#### From Wild Wi-Fi Page:
1. Go to http://127.0.0.1:8080/wild_wifi
2. Click the **"⚙️ Settings"** button (top right in newspaper mode, toolbar in reader mode)

#### Direct URL:
- Newspaper mode: http://127.0.0.1:8080/wild_wifi_settings?view=newspaper
- Reader mode: http://127.0.0.1:8080/wild_wifi_settings?view=reader

### API Endpoints Added

#### 1. GET `/wild_wifi_settings`
Displays the settings page with current prompt and statistics.

#### 2. POST `/api/wild_wifi/update_prompt`
Updates the AI generation prompt.

**Request Body**:
```json
{
  "prompt": "Your custom prompt text here..."
}
```

**Response**:
```json
{
  "success": true,
  "message": "Prompt updated successfully"
}
```

#### 3. POST `/api/wild_wifi/generate_story`
Tests story generation with current prompt (placeholder for future AI integration).

**Response**:
```json
{
  "success": false,
  "error": "AI story generation not yet implemented...",
  "prompt": "Current prompt text"
}
```

### Database Storage

The prompt is stored in the `settings` table:
```sql
INSERT OR REPLACE INTO settings (key, value, updated_at)
VALUES ('wild_wifi_prompt', 'prompt text', CURRENT_TIMESTAMP)
```

### Default Prompt Template

```
Generate a humorous, real-world wireless technology story that is:
- Based on actual wireless/Wi-Fi technology scenarios
- Funny, unexpected, or ironic
- 100-300 words long
- Includes a specific location
- Has a technical insight or lesson
- Suitable for a professional technology audience

The story should highlight the gap between how wireless technology 
is supposed to work and how it actually works in the real world. 
Focus on user behavior, unexpected use cases, or amusing technical mishaps.

Categories: general, business, community, iot, tourism, smart-home

Example themes:
- Wi-Fi password becoming a tourist attraction
- Smart home devices behaving unexpectedly
- Creative solutions to connectivity problems
- Wireless technology in unexpected places
- User behavior around Wi-Fi access
```

### Files Created/Modified

#### New Files:
1. **`app/templates/wild_wifi_settings.html`** - Settings page template
   - Newspaper mode: Rich, colorful design with gradient cards
   - Reader mode: Clean, minimal Google Reader style

#### Modified Files:
1. **`app/main.py`**:
   - Fixed story approval (line ~2478)
   - Fixed refresh endpoint (line ~2527)
   - Added `wild_wifi_settings` route (line ~2537)
   - Added `update_wild_wifi_prompt` endpoint (line ~2560)
   - Added `generate_wild_wifi_story` endpoint (line ~2580)
   - Added `get_default_wild_wifi_prompt()` method (line ~3962)

2. **`app/templates/wild_wifi.html`**:
   - Added Settings button to reader mode toolbar
   - Added Settings button to newspaper mode header

### Future AI Integration

The settings page is ready for AI integration. To add actual story generation:

1. **Choose an AI Provider**:
   - OpenAI GPT-4
   - Anthropic Claude
   - Google Gemini
   - Local LLM (Ollama, LM Studio)

2. **Update the `generate_wild_wifi_story` endpoint**:
   ```python
   # Get the prompt
   prompt = get_prompt_from_db()
   
   # Call AI API
   response = openai.ChatCompletion.create(
       model="gpt-4",
       messages=[{"role": "user", "content": prompt}]
   )
   
   # Parse response and save to database
   story_data = parse_ai_response(response)
   save_story_to_db(story_data)
   ```

3. **Add API Key Configuration**:
   - Store in `.env` file
   - Add to settings page
   - Secure with proper access controls

### Testing

#### Test Story Submission:
1. Go to Wild Wi-Fi page
2. Click "📝 Submit Story"
3. Fill in the form
4. Submit
5. ✅ Story should appear immediately

#### Test Settings Page:
1. Go to Wild Wi-Fi Settings
2. Edit the prompt
3. Click "💾 Save Prompt"
4. ✅ Should see success message
5. Reload page
6. ✅ Prompt should be saved

#### Test Reset to Default:
1. Edit the prompt
2. Click "🔄 Reset to Default"
3. Confirm
4. ✅ Page reloads with default prompt

## Status

✅ **Story Posting** - Fixed and working
✅ **Refresh Endpoint** - Fixed and working
✅ **Settings Page** - Complete and functional
✅ **Prompt Configuration** - Fully implemented
⏳ **AI Generation** - Placeholder ready for integration

## Next Steps (Optional)

1. Integrate with AI API (OpenAI, Claude, etc.)
2. Add batch story generation
3. Add story approval workflow
4. Add prompt templates library
5. Add story editing interface
6. Add analytics dashboard

---

## Quick Links

- Wild Wi-Fi: http://127.0.0.1:8080/wild_wifi
- Settings: http://127.0.0.1:8080/wild_wifi_settings
- Reader Mode: Add `?view=reader` to any URL
