#!/bin/bash

# 🔧 Safe Personal Git Setup for Enhanced KYC Repository
# This script sets repository-specific credentials WITHOUT affecting your Expedia git config

echo "🔒 Enhanced KYC System - Personal Git Configuration"
echo "================================================="
echo ""
echo "This will set up your PERSONAL credentials for this repository only."
echo "Your Expedia git credentials will remain unchanged globally."
echo ""

# Show current global config
echo "🏢 Current Global Git Config (Expedia):"
echo "   Name: $(git config --global user.name)"
echo "   Email: $(git config --global user.email)"
echo ""

echo "📝 Enter Your Personal Details:"
echo "------------------------------"

# Get personal email
while true; do
    read -p "👤 Enter your personal email: " personal_email
    if [[ $personal_email =~ ^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$ ]]; then
        break
    else
        echo "❌ Please enter a valid email address"
    fi
done

# Get personal username
read -p "🏷️  Enter your personal username (for GitHub): " personal_username

echo ""
echo "🔧 Setting up repository-specific configuration..."

# Set local git config (repository-specific only)
git config --local user.name "$personal_username"
git config --local user.email "$personal_email"

echo ""
echo "✅ Repository Configuration Complete!"
echo "====================================="
echo ""
echo "📊 Verification:"
echo "   🏢 Global (Expedia): $(git config --global user.name) <$(git config --global user.email)>"
echo "   🏠 This Repo: $(git config --local user.name) <$(git config --local user.email)>"
echo ""
echo "🎯 What this means:"
echo "   ✅ This repo will use: $personal_username <$personal_email>"
echo "   ✅ Other repos will still use your Expedia credentials"
echo "   ✅ No global configuration was changed"
echo ""

# Check if we need to set up authentication
echo "🔑 Next Steps - Authentication:"
echo "==============================="
echo ""
echo "To push to your personal GitHub repo, you'll need one of these:"
echo ""
echo "Option 1: Personal Access Token (Recommended)"
echo "   1. Go to: https://github.com/settings/tokens"
echo "   2. Click 'Generate new token (classic)'"
echo "   3. Select scopes: 'repo', 'workflow'"
echo "   4. Copy the token when generated"
echo ""
echo "Option 2: GitHub CLI (Easiest)"
echo "   Run: gh auth login"
echo ""

read -p "Do you want to set up authentication now? (y/n): " setup_auth

if [[ $setup_auth =~ ^[Yy]$ ]]; then
    echo ""
    echo "Choose authentication method:"
    echo "1. GitHub CLI (recommended)"
    echo "2. Personal Access Token"
    read -p "Enter choice (1 or 2): " auth_choice
    
    if [[ $auth_choice == "1" ]]; then
        echo "📦 Installing GitHub CLI if needed..."
        if ! command -v gh &> /dev/null; then
            echo "Installing GitHub CLI..."
            brew install gh
        fi
        
        echo "🔐 Authenticating with GitHub CLI..."
        gh auth login
        
        echo "✅ GitHub CLI authentication complete!"
        
    elif [[ $auth_choice == "2" ]]; then
        echo ""
        echo "📋 Personal Access Token Setup:"
        echo "1. Go to: https://github.com/settings/tokens"
        echo "2. Click 'Generate new token (classic)'"
        echo "3. Give it a name like 'Enhanced KYC System'"
        echo "4. Select scopes:"
        echo "   ✅ repo (Full control of private repositories)"
        echo "   ✅ workflow (Update GitHub Action workflows)"
        echo "5. Click 'Generate token'"
        echo "6. Copy the token (you won't see it again!)"
        echo ""
        
        read -p "Enter your Personal Access Token: " -s token
        echo ""
        
        if [[ -n $token ]]; then
            # Store token securely
            echo "protocol=https
host=github.com
username=$personal_username
password=$token" | git credential-osxkeychain store
            
            echo "✅ Personal Access Token stored securely!"
        fi
    fi
fi

echo ""
echo "🚀 Ready to Push Your Enhanced KYC System!"
echo "=========================================="
echo ""
echo "Your enhanced KYC system with fake document detection is ready to be pushed:"
echo ""
echo "🔒 Security Features:"
echo "   ✅ Multi-stage liveness detection"
echo "   ✅ Fake Aadhaar card rejection"  
echo "   ✅ Advanced anti-spoofing measures"
echo "   ✅ Cross-face validation"
echo "   ✅ Document face photo verification"
echo ""
echo "📤 To push your changes:"
echo "   git add ."
echo "   git commit -m '🚀 Enhanced KYC System with Fake Document Detection'"
echo "   git push origin main"
echo ""
echo "🌐 After pushing, you can deploy to:"
echo "   • Railway: ./deploy-railway.sh"
echo "   • Vercel + Render: ./deploy-vercel.sh"
echo ""

# Test the configuration
echo "🧪 Testing git configuration..."
echo "Repository will use: $(git config user.name) <$(git config user.email)>"
echo ""
echo "✅ Setup Complete! Your enhanced KYC system is ready to push! 🎉"
