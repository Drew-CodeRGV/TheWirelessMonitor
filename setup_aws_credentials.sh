#!/bin/bash
# AWS Credentials Setup Helper

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  AWS Credentials Setup                                     ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "You need AWS credentials to deploy to Lightsail."
echo ""
echo "To get your credentials:"
echo "1. Go to: https://console.aws.amazon.com/iam/home#/users"
echo "2. Click your username (or create a new IAM user)"
echo "3. Go to 'Security credentials' tab"
echo "4. Click 'Create access key'"
echo "5. Choose 'Command Line Interface (CLI)'"
echo "6. Copy the Access Key ID and Secret Access Key"
echo ""
echo "Required IAM Permissions:"
echo "  - AmazonLightsailFullAccess (or custom policy)"
echo ""
read -p "Press Enter when you have your credentials ready..."
echo ""

# Run AWS configure
aws configure

echo ""
echo "✅ AWS CLI configured!"
echo ""
echo "Testing connection..."
if aws sts get-caller-identity &> /dev/null; then
    echo "✅ Successfully connected to AWS!"
    echo ""
    aws sts get-caller-identity
    echo ""
    echo "You're ready to deploy! Run:"
    echo "  ./deploy_to_lightsail.sh"
else
    echo "❌ Connection failed. Please check your credentials and try again."
    echo "Run: aws configure"
fi
