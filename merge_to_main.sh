#!/bin/bash

# Merge to Main Script
# This script merges feature/enhancements into main and pushes to GitHub

set -e  # Exit on error

echo "=========================================="
echo "Wireless Monitor - Merge to Main"
echo "=========================================="
echo ""

# Check current branch
CURRENT_BRANCH=$(git branch --show-current)
echo "Current branch: $CURRENT_BRANCH"

# Ensure we're on feature/enhancements
if [ "$CURRENT_BRANCH" != "feature/enhancements" ]; then
    echo "Switching to feature/enhancements..."
    git checkout feature/enhancements
fi

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo ""
    echo "⚠️  You have uncommitted changes:"
    git status --short
    echo ""
    read -p "Do you want to commit these changes? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Enter commit message: " COMMIT_MSG
        git add .
        git commit -m "$COMMIT_MSG"
        git push origin feature/enhancements
        echo "✅ Changes committed and pushed"
    else
        echo "❌ Please commit or stash your changes before merging"
        exit 1
    fi
fi

# Push any remaining commits
echo ""
echo "Pushing feature/enhancements to origin..."
git push origin feature/enhancements
echo "✅ feature/enhancements pushed"

# Switch to main
echo ""
echo "Switching to main branch..."
git checkout main

# Pull latest main
echo "Pulling latest main..."
git pull origin main

# Merge feature/enhancements
echo ""
echo "Merging feature/enhancements into main..."
git merge feature/enhancements -m "Merge feature/enhancements: Newsletter monitoring, reader enhancements, Wild Wi-Fi search, and deployment setup"

# Push main
echo ""
echo "Pushing main to origin..."
git push origin main

echo ""
echo "=========================================="
echo "✅ SUCCESS!"
echo "=========================================="
echo ""
echo "feature/enhancements has been merged into main"
echo "Both branches are now pushed to GitHub"
echo ""
echo "Next steps:"
echo "1. SSH to your Raspberry Pi"
echo "2. Run: cd /path/to/wireless-monitor && git checkout main && git pull origin main"
echo "3. Follow the deployment steps in DEPLOYMENT_AND_MERGE_GUIDE.md"
echo ""
