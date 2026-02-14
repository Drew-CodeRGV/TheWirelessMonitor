# Wild Wi-Fi News Search - Quick Start Guide

## What's New?
Wild Wi-Fi now automatically searches real news sources for funny, unusual, and interesting wireless technology stories!

## How to Use

### 1. Configure Search Keywords
1. Go to: http://localhost:8080/wild_wifi_settings
2. Edit the search keywords (one per line)
3. Click "Save Keywords"

**Default Keywords Include:**
- wifi password funny
- wifi name hilarious
- smart home fail
- router hack creative
- public wifi incident
- And 25 more...

### 2. Search for Stories Manually
1. Go to Wild Wi-Fi Settings page
2. Click "Search for Stories Now" button
3. Wait for search to complete (5-10 seconds)
4. Page will auto-redirect to show new stories

### 3. Automatic Search (Already Running!)
- System automatically searches every 12 hours
- Uses 2-3 random keywords per search
- Runs in background without user action
- New stories appear automatically on Wild Wi-Fi page

## View Stories
Go to: http://localhost:8080/wild_wifi

Stories are organized by:
- **Featured**: Highest quality stories (score > 75)
- **Category**: Password/Name, Smart Home, Router, etc.
- **Quality Score**: 0-100 rating
- **Humor Rating**: 0-10 rating

## Story Categories

### Password/Name Shenanigans
Funny Wi-Fi network names, creative passwords, naming conventions

### Smart Home Mishaps
IoT device failures, smart home automation gone wrong

### Security Shenanigans
Creative hacks, security breaches with humor

### Signal Struggles
Wi-Fi range issues, dead zones, interference problems

### Public Wi-Fi Tales
Airport, cafe, hotel Wi-Fi incidents

### Router Ridiculousness
Router configuration errors, placement issues

### General Wireless Weirdness
Everything else that's funny and wireless-related

## How It Works

### Search Process
1. System picks random keyword from your list
2. Searches DuckDuckGo for news articles
3. Extracts title, URL, and description
4. Checks for duplicates (skips if already exists)
5. Categorizes story based on content
6. Calculates quality and humor scores
7. Saves to database (auto-approved)
8. Updates featured stories

### Scoring System
**Quality Score (0-100):**
- Humor indicators (funny, bizarre, unexpected)
- Story length and detail
- Location and specific details
- Technical relevance

**Humor Rating (0-10):**
- Presence of humor keywords
- Irony and contrast
- Unexpected situations
- Amusing outcomes

## Customization

### Add Your Own Keywords
Think about what makes a good Wild Wi-Fi story:
- **Be Specific**: "wifi password tourist attraction" not just "wifi"
- **Target Humor**: Include words like "funny", "fail", "unusual"
- **Mix Topics**: Cover different areas (smart home, public wifi, router names)
- **One Per Line**: Each line is a complete search phrase

### Example Custom Keywords
```
wifi password museum funny
smart home device ordering things
router name neighborhood war
airport wifi security fail
hotel wifi password creative
coffee shop internet speed complaint
iot device unexpected behavior
mesh network installation fail
```

## Troubleshooting

### No Stories Found?
- Try different/more specific keywords
- Search again later (news sources update constantly)
- Check that keywords are one per line
- Make sure keywords are relevant to wireless/wifi

### Duplicate Stories?
- System automatically prevents duplicates by URL
- If you see duplicates, they're from different sources
- This is normal and shows the story is popular!

### Low Quality Scores?
- System is conservative with scoring
- Stories improve over time as more are added
- Featured stories (75+) are the best ones
- All stories are still interesting and worth reading!

## Advanced Features

### Scheduled Search
- Runs every 12 hours automatically
- Searches 2-3 random keywords per run
- No user action required
- Check logs to see when it runs

### Manual Refresh
- Click "Refresh Stories" on Wild Wi-Fi page
- Re-scores all stories
- Updates featured stories
- Useful after adding many new stories

### Story Management
- All stories auto-approved (approved=1)
- Can manually edit in database if needed
- Featured status updates automatically
- Old stories remain unless manually deleted

## Tips for Best Results

1. **Use Diverse Keywords**: Mix different topics and angles
2. **Be Patient**: Good stories take time to find
3. **Search Regularly**: News changes daily
4. **Review Settings**: Update keywords based on what works
5. **Check Featured**: Best stories automatically highlighted

## Technical Details

### Search Frequency
- **Automatic**: Every 12 hours
- **Manual**: On-demand via button
- **Keywords per Search**: 2-3 random selections

### Data Storage
- **Table**: wild_wifi_stories
- **Auto-Approval**: Yes (approved=1)
- **Deduplication**: By source URL
- **Scoring**: Automatic via WildWiFiCurator

### Search Sources
- Primary: DuckDuckGo Instant Answer API
- Fallback: Sample stories (for testing)
- Extensible: Can add more sources

## Need Help?

### Check Logs
```bash
tail -f logs/app.log | grep "Wild Wi-Fi"
```

### Test Search Manually
```bash
python test_wild_wifi_search.py
```

### View Database
```bash
sqlite3 data/wireless_monitor.db "SELECT title, category, quality_score FROM wild_wifi_stories ORDER BY created_at DESC LIMIT 10;"
```

## What's Next?

The system is fully functional and will continue finding stories automatically. Just:
1. ✅ Configure your preferred keywords
2. ✅ Let it run automatically
3. ✅ Check Wild Wi-Fi page regularly for new stories
4. ✅ Enjoy the funny wireless tales!

---

**Status**: ✅ Fully Operational
**Last Updated**: 2026-02-13
**Version**: 1.0
