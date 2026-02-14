# Merge to Main Script (PowerShell)
# This script merges feature/enhancements into main and pushes to GitHub

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Wireless Monitor - Merge to Main" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check current branch
$currentBranch = git branch --show-current
Write-Host "Current branch: $currentBranch" -ForegroundColor Yellow

# Ensure we're on feature/enhancements
if ($currentBranch -ne "feature/enhancements") {
    Write-Host "Switching to feature/enhancements..." -ForegroundColor Yellow
    git checkout feature/enhancements
}

# Check for uncommitted changes
$status = git status --porcelain
if ($status) {
    Write-Host ""
    Write-Host "⚠️  You have uncommitted changes:" -ForegroundColor Yellow
    git status --short
    Write-Host ""
    $commit = Read-Host "Do you want to commit these changes? (y/n)"
    if ($commit -eq "y" -or $commit -eq "Y") {
        $commitMsg = Read-Host "Enter commit message"
        git add .
        git commit -m $commitMsg
        git push origin feature/enhancements
        Write-Host "✅ Changes committed and pushed" -ForegroundColor Green
    } else {
        Write-Host "❌ Please commit or stash your changes before merging" -ForegroundColor Red
        exit 1
    }
}

# Push any remaining commits
Write-Host ""
Write-Host "Pushing feature/enhancements to origin..." -ForegroundColor Yellow
git push origin feature/enhancements
Write-Host "✅ feature/enhancements pushed" -ForegroundColor Green

# Switch to main
Write-Host ""
Write-Host "Switching to main branch..." -ForegroundColor Yellow
git checkout main

# Pull latest main
Write-Host "Pulling latest main..." -ForegroundColor Yellow
git pull origin main

# Merge feature/enhancements
Write-Host ""
Write-Host "Merging feature/enhancements into main..." -ForegroundColor Yellow
git merge feature/enhancements -m "Merge feature/enhancements: Newsletter monitoring, reader enhancements, Wild Wi-Fi search, and deployment setup"

# Push main
Write-Host ""
Write-Host "Pushing main to origin..." -ForegroundColor Yellow
git push origin main

Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "✅ SUCCESS!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "feature/enhancements has been merged into main" -ForegroundColor Green
Write-Host "Both branches are now pushed to GitHub" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. SSH to your Raspberry Pi" -ForegroundColor White
Write-Host "2. Run: cd /path/to/wireless-monitor && git checkout main && git pull origin main" -ForegroundColor White
Write-Host "3. Follow the deployment steps in DEPLOYMENT_AND_MERGE_GUIDE.md" -ForegroundColor White
Write-Host ""
