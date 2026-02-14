# Gmail Setup for Newsletter Monitor

## The Issue
Gmail authentication failed with your current password. This is normal - Gmail requires special setup for IMAP access.

## Solution: Create an App Password

### Step 1: Enable 2-Step Verification (if not already enabled)
1. Go to https://myaccount.google.com/security
2. Click "2-Step Verification"
3. Follow the prompts to enable it
4. You'll need your phone for verification

### Step 2: Create App Password
1. Go to https://myaccount.google.com/apppasswords
   - Or: Google Account → Security → 2-Step Verification → App passwords
2. Select app: **Mail**
3. Select device: **Windows Computer** (or Other)
4. Click **Generate**
5. Google will show a 16-character password like: `abcd efgh ijkl mnop`
6. **Copy this password** (you won't see it again!)

### Step 3: Enable IMAP
1. Go to Gmail → Settings (gear icon) → See all settings
2. Click "Forwarding and POP/IMAP" tab
3. Under "IMAP access", select **Enable IMAP**
4. Click **Save Changes**

### Step 4: Test Connection
Once you have the app password, run:

```bash
python test_email_connection.py
```

Then update the password in the script to your new app password.

## Alternative: Update Password in Script

Edit `test_email_connection.py` and replace the password:

```python
password = "your 16 character app password here"
```

## Quick Links
- Enable 2FA: https://myaccount.google.com/signinoptions/two-step-verification
- App Passwords: https://myaccount.google.com/apppasswords
- Gmail Settings: https://mail.google.com/mail/u/0/#settings/fwdandpop

## Once Working

After you get the app password and the test succeeds, you can:

1. **One-time check:**
```bash
python email_newsletter_monitor.py wifinewsletters@gmail.com "your_app_password" imap.gmail.com
```

2. **Run continuously (checks every 30 minutes):**
```bash
python email_newsletter_monitor.py
# Enter email: wifinewsletters@gmail.com
# Enter password: your_app_password
# Enter server: imap.gmail.com
# Select mode: 2
# Interval: 30
```

## Security Note
The app password is ONLY for this application. Your main Gmail password remains secure and unchanged.
