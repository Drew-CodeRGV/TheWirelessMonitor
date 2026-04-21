# How to Get Admin AWS Credentials

You need admin credentials to create IAM policies. Here are your options:

## Option 1: Use AWS Root Account (Easiest)

Your root account is the email/password you used to sign up for AWS.

### Step 1: Log into AWS Console
Go to: https://console.aws.amazon.com/
- Use your root account email and password

### Step 2: Create Access Keys for Root
1. Click your account name (top right) → **Security credentials**
2. Scroll down to **Access keys** section
3. Click **Create access key**
4. Choose **Command Line Interface (CLI)**
5. Check "I understand..." and click **Next**
6. Click **Create access key**
7. **IMPORTANT**: Copy both:
   - Access key ID (starts with AKIA...)
   - Secret access key (long random string)
   - Download the CSV file as backup

### Step 3: Use These Credentials
Run:
```bash
./setup_permissions_with_admin.sh
```

When prompted, enter:
- Access Key ID: (paste the AKIA... key)
- Secret Access Key: (paste the secret)
- Region: us-east-1
- Output format: json

---

## Option 2: Create an Admin IAM User

If you don't want to use root credentials, create an admin IAM user.

### Step 1: Log into AWS Console as Root
https://console.aws.amazon.com/

### Step 2: Create Admin User
1. Go to: https://console.aws.amazon.com/iam/home#/users
2. Click **Create user**
3. Username: `admin-user` (or any name)
4. Click **Next**

### Step 3: Attach Admin Policy
1. Select **Attach policies directly**
2. Search for: `AdministratorAccess`
3. Check the box next to it
4. Click **Next**
5. Click **Create user**

### Step 4: Create Access Keys
1. Click on the user you just created
2. Go to **Security credentials** tab
3. Scroll to **Access keys**
4. Click **Create access key**
5. Choose **Command Line Interface (CLI)**
6. Check "I understand..." and click **Next**
7. Click **Create access key**
8. Copy both keys (or download CSV)

### Step 5: Use These Credentials
Run:
```bash
./setup_permissions_with_admin.sh
```

---

## Option 3: Use Existing Admin User

If you already have an admin IAM user but don't have access keys:

### Step 1: Log into AWS Console
https://console.aws.amazon.com/

### Step 2: Go to Your Admin User
1. Go to: https://console.aws.amazon.com/iam/home#/users
2. Click on your admin username
3. Go to **Security credentials** tab

### Step 3: Create Access Keys
1. Scroll to **Access keys** section
2. Click **Create access key**
3. Choose **Command Line Interface (CLI)**
4. Check "I understand..." and click **Next**
5. Click **Create access key**
6. Copy both keys

### Step 4: Use These Credentials
Run:
```bash
./setup_permissions_with_admin.sh
```

---

## Security Best Practices

### After Setup is Complete

Once you've run `./setup_permissions_with_admin.sh` successfully:

1. **Delete the admin access keys** (if you used root):
   - Go to: https://console.aws.amazon.com/iam/home#/security_credentials
   - Find the access key you created
   - Click **Actions** → **Delete**

2. **Or keep them secure**:
   - Store in password manager
   - Never commit to git
   - Never share

### Why Root Access Keys Are Risky

Root account has unlimited access to everything in AWS:
- Can delete all resources
- Can rack up huge bills
- Can access billing info
- Can close the account

That's why we only use them temporarily to set up permissions, then delete them.

---

## Troubleshooting

### "I don't know my root password"
1. Go to: https://console.aws.amazon.com/
2. Click **Forgot password?**
3. Enter your root email
4. Follow reset instructions

### "I don't have access to the root email"
You'll need to contact AWS Support to recover your account.

### "I created keys but they don't work"
- Wait 30 seconds for AWS to activate them
- Make sure you copied both the Access Key ID and Secret Access Key
- Check for extra spaces when pasting

### "I'm getting 'Access Denied' errors"
The user you're using doesn't have admin permissions. You need:
- Root account credentials, OR
- IAM user with `AdministratorAccess` policy attached

---

## Quick Reference

### What You Need
- **Access Key ID**: Starts with `AKIA...` (20 characters)
- **Secret Access Key**: Long random string (40 characters)
- **Region**: `us-east-1` (or your preferred region)

### Where to Get Them
- Root: https://console.aws.amazon.com/ → Security credentials
- IAM User: https://console.aws.amazon.com/iam/home#/users → [username] → Security credentials

### What to Run
```bash
./setup_permissions_with_admin.sh
```

This will:
1. Ask for admin credentials
2. Create Lightsail policy
3. Attach to drew-signal user
4. Test that it works

Then you can deploy:
```bash
./deploy_to_lightsail.sh
```

---

## Alternative: Just Use AWS Console

If getting admin CLI credentials is too complicated, you can do everything in the web console:

See: `CONSOLE_POLICY_SETUP.md`

It takes 7 minutes and doesn't require CLI access.
