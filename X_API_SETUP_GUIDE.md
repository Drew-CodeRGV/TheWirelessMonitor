# X API Setup Guide - Complete Instructions

## Current Implementation Status

✅ **COMPLETE** - App-only authentication implemented
✅ **PUBLIC DATA ONLY** - Fetches from configured public accounts
✅ **CONFIGURABLE** - Account lists in `x_accounts_config.json`
✅ **BEARER TOKEN ONLY** - No OAuth user tokens needed

## What You Need

**Only 1 credential required**: Bearer Token

That's it! No access tokens, no OAuth flow, no personal account exposure.

## Why Bearer Token Only?

The implementation uses **app-only authentication** which:
- ✅ Fetches public data from specified accounts
- ✅ Doesn't access your personal timeline
- ✅ Doesn't expose your account information
- ✅ Simpler setup (just one token)
- ✅ More secure (no personal data)

## How to Get Your Bearer Token

### Step 1: Go to X Developer Portal
Visit: https://developer.twitter.com/en/portal/dashboard

### Step 2: Create or Select Your App
- If you don't have an app, click "Create App"
- If you have an app, click on its name

### Step 3: Go to Keys and Tokens
Click the **"Keys and tokens"** tab

### Step 4: Copy Bearer Token
1. Scroll to **"Bearer Token"** section
2. If you don't see one, click **"Generate"**
3. Copy the token (looks like: `AAAAAAAAAAAAAAAAAAAAANtR7gEA...`)
4. **IMPORTANT**: Save it securely - you can't see it again!

### Step 5: Update Your .env File

Open `.env` and add:

```env
# X (Twitter) API Credentials
X_BEARER_TOKEN=your_bearer_token_here
```

**Note**: You can remove the other X credentials if you have them - they're not needed.

### Step 6: Customize Accounts (Optional)

Edit `x_accounts_config.json` to add/remove accounts:

```json
{
  "following_accounts": [
    "TechCrunch",
    "WIRED",
    "YourFavoriteAccount"
  ],
  "followers_accounts": [
    "5GTechnologyWorld",
    "AnotherAccount"
  ]
}
```

### Step 7: Restart the Application

```bash
# Stop the current process (Ctrl+C)
# Then restart:
python app/main.py
```

### Step 8: Test It

1. Visit http://localhost:8080
2. Scroll to the X Timeline section
3. Click "🔄 Refresh"
4. You should see "Live" mode indicator
5. Real tweets from your configured accounts!

## What This Implementation Does

### Fetches From Public Accounts
- Loads account lists from `x_accounts_config.json`
- Fetches recent tweets from each account
- Scores by engagement and relevance
- Shows top 3 tweets and articles from each group

### Does NOT Access
- ❌ Your personal timeline
- ❌ Your DMs or private data
- ❌ Your followers or following lists
- ❌ Your account information

### Benefits
- ✅ Simple setup (one token)
- ✅ No personal data exposure
- ✅ Easy to customize accounts
- ✅ Sufficient for monitoring public tech news

## API Costs

- **Free Tier**: 500 reads/month (very limited)
- **Basic Tier**: $100/month - 10,000 reads/month (recommended)
- **Each refresh**: ~10 API calls
- **Monthly refreshes**: ~1,000 times on Basic tier

## Troubleshooting

### Still Seeing Mock Data?
1. Check `.env` has `X_BEARER_TOKEN=...`
2. Restart the application
3. Check logs for error messages
4. Verify Bearer Token is valid (not expired)

### Error: "401 Unauthorized"
- Bearer Token is invalid or expired
- Regenerate token in X Developer Portal
- Update `.env` with new token
- Restart application

### Error: "429 Too Many Requests"
- You've hit rate limits
- Wait 15 minutes and try again
- Consider reducing refresh frequency
- Upgrade to higher tier if needed

### No Tweets Showing
- Check account usernames in `x_accounts_config.json`
- Verify accounts exist and are public
- Check logs for specific errors
- Try with default accounts first

### Want to Add More Accounts?
1. Edit `x_accounts_config.json`
2. Add usernames to appropriate list
3. Save file
4. Refresh timeline (no restart needed)

## Security Reminder

🚨 **REGENERATE YOUR CREDENTIALS** 🚨

Since you shared credentials publicly in chat, you should:
1. Go to X Developer Portal
2. Regenerate Bearer Token
3. Update `.env` with new token
4. Never share credentials publicly again

The `.gitignore` file protects `.env` from being committed to git.

## Alternative: Use Mock Data

If you don't want to pay for X API access, the mock data works great! It shows realistic examples of tech/wireless news tweets. Just don't add the Bearer Token to `.env`.

---

**Need help?** Check the application logs for detailed error messages.
**Questions?** The implementation is complete and ready to use with just a Bearer Token!
