# Gmail API Setup Guide (Modern Method)

## Why Gmail API Instead of IMAP?

Google has restricted IMAP/POP access for certain account types. The Gmail API is the modern, recommended approach that works with ALL Gmail accounts including:
- Personal Gmail accounts
- Google Workspace accounts
- Accounts with advanced security
- Accounts with 2FA

## Setup Steps

### Step 1: Install Required Packages

```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### Step 2: Create Google Cloud Project

1. Go to https://console.cloud.google.com/
2. Click "Select a project" → "New Project"
3. Name it "Wireless Monitor" or similar
4. Click "Create"

### Step 3: Enable Gmail API

1. In your project, go to "APIs & Services" → "Library"
2. Search for "Gmail API"
3. Click on it and click "Enable"

### Step 4: Create OAuth Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. If prompted, configure OAuth consent screen:
   - User Type: **External**
   - App name: **Wireless Monitor**
   - User support email: **your email**
   - Developer contact: **your email**
   - Click "Save and Continue"
   - Scopes: Skip (click "Save and Continue")
   - Test users: Add **wifinewsletters@gmail.com**
   - Click "Save and Continue"
4. Back to Create OAuth client ID:
   - Application type: **Desktop app**
   - Name: **Wireless Monitor Desktop**
   - Click "Create"
5. Click "Download JSON"
6. Save the file as `credentials.json` in your Wireless Monitor directory

### Step 5: Run the Monitor

```bash
python gmail_api_newsletter_monitor.py
```

**First Run:**
- A browser window will open
- Sign in with **wifinewsletters@gmail.com**
- Click "Continue" when warned about unverified app (this is your own app)
- Click "Allow" to grant permissions
- Browser will show "The authentication flow has completed"
- Close the browser and return to terminal

**Subsequent Runs:**
- No browser needed - uses saved token
- Token stored in `token.json`

### Step 6: Choose Mode

1. **One-time check** - Checks once and exits
2. **Continuous monitoring** - Checks every X minutes

## File Structure

After setup, you'll have:
```
credentials.json  ← OAuth credentials (keep secret!)
token.json        ← Access token (auto-generated)
gmail_api_newsletter_monitor.py  ← The script
```

## Security Notes

- **credentials.json**: Contains your OAuth client secret - keep it private!
- **token.json**: Contains your access token - keep it private!
- Add both to `.gitignore` if using git
- Never share these files

## Troubleshooting

### "credentials.json not found"
- Download OAuth credentials from Google Cloud Console
- Save as `credentials.json` in the same directory as the script

### "Access blocked: This app's request is invalid"
- Make sure you added wifinewsletters@gmail.com as a test user
- Check OAuth consent screen configuration

### "The app is not verified"
- This is normal for personal projects
- Click "Advanced" → "Go to Wireless Monitor (unsafe)"
- This is YOUR app, so it's safe

### "Invalid grant" or "Token expired"
- Delete `token.json`
- Run script again to re-authenticate

## Advantages Over IMAP

✅ Works with ALL Gmail account types
✅ No app passwords needed
✅ More secure (OAuth 2.0)
✅ Better rate limits
✅ Access to Gmail features
✅ Officially supported by Google

## Quick Start Commands

**One-time check:**
```bash
python gmail_api_newsletter_monitor.py
# Select: 1
```

**Continuous (every 30 minutes):**
```bash
python gmail_api_newsletter_monitor.py
# Select: 2
# Interval: 30
```

**Stop continuous monitoring:**
Press `Ctrl+C`

## What It Does

1. Connects to Gmail using OAuth
2. Searches for unread emails
3. Identifies newsletters by subject/sender
4. Extracts article links from email HTML
5. Calculates relevance scores
6. Saves articles to Wireless Monitor database
7. Articles appear at http://localhost:8080

## Next Steps

After setup:
1. Subscribe to wireless technology newsletters
2. Send them to wifinewsletters@gmail.com
3. Run the monitor
4. Articles automatically appear in Wireless Monitor!

## Recommended Newsletters

Subscribe to these at wifinewsletters@gmail.com:
- TechCrunch Daily
- The Verge Newsletter
- Ars Technica Newsletter
- IEEE Spectrum Digest
- Fierce Wireless Updates
- RCR Wireless News
- Engadget Newsletter
- Wired Technology

## Support

If you encounter issues:
1. Check credentials.json exists
2. Verify Gmail API is enabled
3. Check test user is added
4. Delete token.json and re-authenticate
5. Check console for error messages
