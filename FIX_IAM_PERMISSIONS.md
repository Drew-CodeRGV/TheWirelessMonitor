# Fix IAM Permissions Error

## The Problem

Your IAM user `drew-signal` doesn't have permission to use Lightsail.

Error:
```
User: arn:aws:iam::627002024328:user/drew-signal is not authorized to perform: 
lightsail:CreateKeyPair because no identity-based policy allows the lightsail:CreateKeyPair action
```

## Quick Fix (AWS Console - Easiest)

### Step 1: Go to IAM Console
Open: https://console.aws.amazon.com/iam/home#/users/drew-signal

### Step 2: Add Permissions
1. Click the **"Add permissions"** button
2. Select **"Attach policies directly"**
3. In the search box, type: `AmazonLightsailFullAccess`
4. Check the box next to **"AmazonLightsailFullAccess"**
5. Click **"Add permissions"** button at the bottom

### Step 3: Verify
Run this to verify it worked:
```bash
aws lightsail get-regions
```

If you see a list of regions, you're good to go!

### Step 4: Deploy
```bash
./deploy_to_lightsail.sh
```

---

## Alternative: Use CLI (If you have admin access)

### Option A: Run the fix script
```bash
./fix_iam_permissions.sh
```

### Option B: Manual command
```bash
aws iam attach-user-policy \
    --user-name drew-signal \
    --policy-arn arn:aws:iam::aws:policy/AmazonLightsailFullAccess
```

---

## What Permissions Are Needed?

The `AmazonLightsailFullAccess` policy includes:
- ✅ Create/delete instances
- ✅ Create/manage static IPs
- ✅ Create/manage key pairs
- ✅ Configure firewall rules
- ✅ Create snapshots
- ✅ View metrics and logs

This is the AWS-managed policy specifically for Lightsail.

---

## Minimal Permissions (If you want to be restrictive)

If you don't want full access, here's a minimal policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "lightsail:CreateInstances",
                "lightsail:CreateKeyPair",
                "lightsail:GetKeyPair",
                "lightsail:GetInstance",
                "lightsail:GetInstances",
                "lightsail:AllocateStaticIp",
                "lightsail:AttachStaticIp",
                "lightsail:GetStaticIp",
                "lightsail:PutInstancePublicPorts",
                "lightsail:CreateInstanceSnapshot",
                "lightsail:GetInstanceState"
            ],
            "Resource": "*"
        }
    ]
}
```

To add this custom policy:
1. Go to IAM → Policies → Create policy
2. Click JSON tab
3. Paste the above
4. Name it: `LightsailDeploymentPolicy`
5. Attach it to user `drew-signal`

---

## Troubleshooting

### "I don't have IAM permissions"
You need to log in with:
- Your AWS root account, OR
- An IAM user with `IAMFullAccess` or admin permissions

### "I'm using the root account"
Root accounts have all permissions by default. If you're getting this error with root:
1. Make sure you're using the right AWS account
2. Check: `aws sts get-caller-identity`

### "I want to use a different IAM user"
```bash
# Configure a different profile
aws configure --profile admin

# Then use it to fix permissions
aws iam attach-user-policy \
    --user-name drew-signal \
    --policy-arn arn:aws:iam::aws:policy/AmazonLightsailFullAccess \
    --profile admin
```

---

## After Fixing Permissions

Test that it works:
```bash
# This should return a list of regions
aws lightsail get-regions

# This should show your account info
aws sts get-caller-identity
```

Then deploy:
```bash
./deploy_to_lightsail.sh
```

---

## Security Best Practice

After deployment is complete, if you want to restrict permissions:
1. Detach `AmazonLightsailFullAccess`
2. Attach a read-only policy: `AmazonLightsailReadOnlyAccess`
3. This prevents accidental deletions while allowing monitoring

```bash
# Remove full access
aws iam detach-user-policy \
    --user-name drew-signal \
    --policy-arn arn:aws:iam::aws:policy/AmazonLightsailFullAccess

# Add read-only access
aws iam attach-user-policy \
    --user-name drew-signal \
    --policy-arn arn:aws:iam::aws:policy/AmazonLightsailReadOnlyAccess
```
