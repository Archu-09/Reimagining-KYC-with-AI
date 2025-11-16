#!/bin/bash

# Complete KYC System Setup Script
echo "🚀 Setting up Complete KYC System with OAuth and Liveness Detection..."

# Check if required tools are installed
command -v docker >/dev/null 2>&1 || { echo "❌ Docker is required but not installed. Aborting." >&2; exit 1; }
command -v node >/dev/null 2>&1 || { echo "❌ Node.js is required but not installed. Aborting." >&2; exit 1; }

echo "✅ Prerequisites check passed"

# Create environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating environment configuration..."
    cp .env.example .env
    echo "⚠️  Please update .env with your OAuth credentials before running the system"
fi

# Install backend dependencies
echo "📦 Installing Python dependencies..."
cd backend
if [ -f requirements.txt ]; then
    pip install -r requirements.txt
else
    echo "❌ requirements.txt not found in backend directory"
    exit 1
fi
cd ..

# Install frontend dependencies  
echo "📦 Installing Node.js dependencies..."
cd frontend
if [ -f package.json ]; then
    npm install
else
    echo "❌ package.json not found in frontend directory"
    exit 1
fi
cd ..

# Build Docker containers
echo "🐳 Building Docker containers..."
docker-compose build

# Start the system
echo "🚀 Starting KYC system..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check service health
echo "🔍 Checking service health..."
if curl -f http://localhost:8000/ >/dev/null 2>&1; then
    echo "✅ Backend is running at http://localhost:8000"
else
    echo "❌ Backend is not responding"
fi

if curl -f http://localhost:3000/ >/dev/null 2>&1; then
    echo "✅ Frontend is running at http://localhost:3000"
else
    echo "❌ Frontend is not responding"
fi

echo ""
echo "🎉 KYC System Setup Complete!"
echo ""
echo "🔗 Access Points:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   Admin Panel: http://localhost:3000/admin"
echo ""
echo "📚 Next Steps:"
echo "   1. Update .env with your OAuth credentials (Google, GitHub)"
echo "   2. Visit http://localhost:3000 to start KYC verification"
echo "   3. Test OAuth sign-in with your configured providers"
echo "   4. Try the advanced liveness detection feature"
echo ""
echo "🔧 OAuth Setup:"
echo "   - Google: https://console.developers.google.com/"
echo "   - GitHub: https://github.com/settings/applications/new"
echo "   - Set redirect URIs to: http://localhost:3000/auth/callback/{provider}"
echo ""
echo "📖 Documentation: Check README.md and DOCUMENTATION_INDEX.md"
