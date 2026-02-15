#!/bin/bash
# Fix IAM permissions for Lightsail deployment

echo "🔧 Fixing IAM Permissions for Lightsail"
echo ""

IAM_USER="drew-signal"
POLICY_NAME="LightsailFullAccessPolicy"

echo "This script will attach the AmazonLightsailFullAccess policy to user: $IAM_USER"
echo ""
echo "⚠️  You need to run this with an AWS account that has IAM permissions"
echo "    (typically your root account or an admin user)"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 1
fi

echo ""
echo "Attaching AmazonLightsailFullAccess policy..."

# Attach AWS managed policy for Lightsail
aws iam attach-user-policy \
    --user-name "$IAM_USER" \
    --policy-arn "arn:aws:iam::aws:policy/AmazonLightsailFullAccess"

if [ $? -eq 0 ]; then
    echo "✅ Policy attached successfully!"
    echo ""
    echo "The user $IAM_USER now has full Lightsail access."
    echo "You can now run: ./deploy_to_lightsail.sh"
else
    echo ""
    echo "❌ Failed to attach policy. You may need to:"
    echo ""
    echo "Option 1: Use AWS Console (Easier)"
    echo "  1. Go to: https://console.aws.amazon.com/iam/home#/users/$IAM_USER"
    echo "  2. Click 'Add permissions' → 'Attach policies directly'"
    echo "  3. Search for 'AmazonLightsailFullAccess'"
    echo "  4. Check the box and click 'Add permissions'"
    echo ""
    echo "Option 2: Use a different AWS profile with admin access"
    echo "  aws iam attach-user-policy \\"
    echo "    --user-name $IAM_USER \\"
    echo "    --policy-arn arn:aws:iam::aws:policy/AmazonLightsailFullAccess \\"
    echo "    --profile YOUR_ADMIN_PROFILE"
    echo ""
fi
