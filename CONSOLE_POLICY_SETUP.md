# Create Lightsail Policy via AWS Console

Since `AmazonLightsailFullAccess` isn't available in your account, you need to create a custom policy.

## Step-by-Step Guide (AWS Console)

### Step 1: Create the Policy

1. **Go to IAM Policies**: https://console.aws.amazon.com/iam/home#/policies

2. **Click "Create policy"** button

3. **Click the "JSON" tab**

4. **Paste this policy**:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "lightsail:*"
            ],
            "Resource": "*"
        }
    ]
}
```

5. **Click "Next"**

6. **Name the policy**: `LightsailDeploymentPolicy`

7. **Description**: `Full access to Lightsail for deployment`

8. **Click "Create policy"**

### Step 2: Attach Policy to User

1. **Go to IAM Users**: https://console.aws.amazon.com/iam/home#/users/drew-signal

2. **Click "Add permissions"** button

3. **Select "Attach policies directly"**

4. **Search for**: `LightsailDeploymentPolicy` (the policy you just created)

5. **Check the box** next to it

6. **Click "Add permissions"**

### Step 3: Test It

Wait 30 seconds for permissions to propagate, then run:
```bash
aws lightsail get-regions
```

You should see a list of AWS regions.

### Step 4: Deploy!

```bash
./deploy_to_lightsail.sh
```

---

## Alternative: Use CLI Script

If you have IAM permissions via CLI, run:
```bash
./create_lightsail_policy.sh
```

This will create and attach the policy automatically.

---

## What This Policy Does

The policy `lightsail:*` gives full access to all Lightsail operations:
- ✅ Create/delete instances
- ✅ Manage static IPs
- ✅ Create key pairs
- ✅ Configure firewall
- ✅ Create snapshots
- ✅ View metrics

This is equivalent to the AWS-managed `AmazonLightsailFullAccess` policy.

---

## Minimal Permissions (If you want to be more restrictive)

If you only want deployment permissions (no delete), use this policy instead:

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
                "lightsail:GetKeyPairs",
                "lightsail:GetInstance",
                "lightsail:GetInstances",
                "lightsail:GetInstanceState",
                "lightsail:AllocateStaticIp",
                "lightsail:AttachStaticIp",
                "lightsail:GetStaticIp",
                "lightsail:GetStaticIps",
                "lightsail:GetRegions",
                "lightsail:GetBlueprints",
                "lightsail:GetBundles",
                "lightsail:PutInstancePublicPorts",
                "lightsail:GetInstancePortStates",
                "lightsail:CreateInstanceSnapshot",
                "lightsail:GetInstanceSnapshot",
                "lightsail:GetInstanceSnapshots",
                "lightsail:CreateInstancesFromSnapshot"
            ],
            "Resource": "*"
        }
    ]
}
```

This allows deployment but prevents accidental deletion of resources.

---

## Troubleshooting

### "I don't see the policy I created"
- Wait 30 seconds and refresh the page
- Make sure you're in the right AWS account
- Check the policy was created: https://console.aws.amazon.com/iam/home#/policies

### "Access Denied when creating policy"
You need IAM permissions to create policies. Options:
1. Ask your AWS admin to create the policy
2. Use an AWS account with admin access
3. Log in with your root account

### "Still getting permission errors after attaching"
- Wait 1-2 minutes for AWS to propagate permissions
- Log out and log back in to AWS CLI: `aws configure`
- Verify the policy is attached:
  ```bash
  aws iam list-attached-user-policies --user-name drew-signal
  ```

---

## After Setup

Once permissions are working, deploy with:
```bash
./deploy_to_lightsail.sh
```

The script will handle everything else automatically!
