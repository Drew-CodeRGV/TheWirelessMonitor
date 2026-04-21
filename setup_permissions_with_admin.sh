#!/bin/bash
# Setup Lightsail permissions using an admin account

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  Setup Lightsail Permissions via Admin Account            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "This script will:"
echo "  1. Configure an admin AWS profile"
echo "  2. Create the Lightsail policy"
echo "  3. Attach it to drew-signal user"
echo ""
echo "You need AWS credentials with IAM permissions (root or admin user)"
echo ""
read -p "Do you have admin AWS credentials? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Please get admin credentials and run this script again."
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Configuring admin AWS profile..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Enter your ADMIN AWS credentials (not drew-signal):"
echo ""

# Configure admin profile
aws configure --profile admin

echo ""
echo "Testing admin credentials..."
ADMIN_USER=$(aws sts get-caller-identity --profile admin --query 'Arn' --output text 2>&1)

if [[ $ADMIN_USER == arn:aws:* ]]; then
    echo "✅ Admin credentials working: $ADMIN_USER"
else
    echo "❌ Admin credentials failed. Error:"
    echo "$ADMIN_USER"
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Creating Lightsail policy..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Create policy JSON
cat > /tmp/lightsail-policy.json << 'EOF'
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
EOF

POLICY_NAME="LightsailDeploymentPolicy"
IAM_USER="drew-signal"

# Try to create policy
POLICY_ARN=$(aws iam create-policy \
    --profile admin \
    --policy-name "$POLICY_NAME" \
    --policy-document file:///tmp/lightsail-policy.json \
    --description "Full access to Lightsail for deployment" \
    --query 'Policy.Arn' \
    --output text 2>&1)

if [[ $POLICY_ARN == arn:aws:iam::* ]]; then
    echo "✅ Policy created: $POLICY_ARN"
elif [[ $POLICY_ARN == *"EntityAlreadyExists"* ]]; then
    echo "ℹ️  Policy already exists, getting ARN..."
    ACCOUNT_ID=$(aws sts get-caller-identity --profile admin --query Account --output text)
    POLICY_ARN="arn:aws:iam::${ACCOUNT_ID}:policy/${POLICY_NAME}"
    echo "✅ Using existing policy: $POLICY_ARN"
else
    echo "❌ Failed to create policy:"
    echo "$POLICY_ARN"
    rm -f /tmp/lightsail-policy.json
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Attaching policy to user: $IAM_USER"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

aws iam attach-user-policy \
    --profile admin \
    --user-name "$IAM_USER" \
    --policy-arn "$POLICY_ARN"

if [ $? -eq 0 ]; then
    echo "✅ Policy attached successfully!"
else
    echo "❌ Failed to attach policy"
    rm -f /tmp/lightsail-policy.json
    exit 1
fi

# Cleanup
rm -f /tmp/lightsail-policy.json

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Testing permissions..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Waiting 5 seconds for AWS to propagate permissions..."
sleep 5

# Test with drew-signal credentials (default profile)
if aws lightsail get-regions &> /dev/null; then
    echo "✅ Permissions working!"
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║  ✅ SUCCESS! Ready to deploy                               ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
    echo "Run: ./deploy_to_lightsail.sh"
    echo ""
else
    echo "⏳ Permissions may take up to 60 seconds to propagate."
    echo ""
    echo "Wait a minute, then test with:"
    echo "  aws lightsail get-regions"
    echo ""
    echo "Once that works, run:"
    echo "  ./deploy_to_lightsail.sh"
fi
