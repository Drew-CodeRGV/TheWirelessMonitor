#!/bin/bash
# Create custom Lightsail deployment policy

echo "🔧 Creating Custom Lightsail Deployment Policy"
echo ""

POLICY_NAME="LightsailDeploymentPolicy"
IAM_USER="drew-signal"

# Create the policy JSON
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

echo "Creating IAM policy: $POLICY_NAME"
echo ""

# Create the policy
POLICY_ARN=$(aws iam create-policy \
    --policy-name "$POLICY_NAME" \
    --policy-document file:///tmp/lightsail-policy.json \
    --description "Full access to Lightsail for deployment" \
    --query 'Policy.Arn' \
    --output text 2>&1)

if [[ $POLICY_ARN == arn:aws:iam::* ]]; then
    echo "✅ Policy created: $POLICY_ARN"
    echo ""
    echo "Attaching policy to user: $IAM_USER"
    
    aws iam attach-user-policy \
        --user-name "$IAM_USER" \
        --policy-arn "$POLICY_ARN"
    
    if [ $? -eq 0 ]; then
        echo "✅ Policy attached successfully!"
        echo ""
        echo "Testing permissions..."
        sleep 2
        
        if aws lightsail get-regions &> /dev/null; then
            echo "✅ Permissions working! You can now deploy."
            echo ""
            echo "Run: ./deploy_to_lightsail.sh"
        else
            echo "⏳ Permissions may take a few seconds to propagate. Try again in 30 seconds."
        fi
    else
        echo "❌ Failed to attach policy"
    fi
elif [[ $POLICY_ARN == *"EntityAlreadyExists"* ]]; then
    echo "ℹ️  Policy already exists. Attaching to user..."
    
    # Get account ID
    ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    POLICY_ARN="arn:aws:iam::${ACCOUNT_ID}:policy/${POLICY_NAME}"
    
    aws iam attach-user-policy \
        --user-name "$IAM_USER" \
        --policy-arn "$POLICY_ARN"
    
    if [ $? -eq 0 ]; then
        echo "✅ Policy attached successfully!"
        echo ""
        echo "Run: ./deploy_to_lightsail.sh"
    else
        echo "❌ Failed to attach policy"
    fi
else
    echo "❌ Failed to create policy"
    echo ""
    echo "Error: $POLICY_ARN"
    echo ""
    echo "You may need to use the AWS Console method instead:"
    echo "See: FIX_IAM_PERMISSIONS.md"
fi

# Cleanup
rm -f /tmp/lightsail-policy.json
