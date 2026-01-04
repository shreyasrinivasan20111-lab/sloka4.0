#!/bin/bash

# Sloka 4.0 - Vercel Deployment Script
# This script prepares and deploys the application to Vercel

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Sloka 4.0 - Vercel Deployment${NC}"
echo "=================================="

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo -e "${RED}❌ Vercel CLI not found${NC}"
    echo "Install it with: npm install -g vercel"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  No .env file found${NC}"
    echo "Please create .env file based on .env.example"
    exit 1
fi

echo -e "${BLUE}📋 Pre-deployment checklist:${NC}"
echo "✓ Vercel CLI installed"
echo "✓ Environment file exists"

# Ask for confirmation
echo -e "\n${YELLOW}🤔 Ready to deploy to Vercel?${NC}"
echo "Make sure you have:"
echo "  - Set up your production database (Neon/Vercel Postgres)"
echo "  - Configured Vercel Blob storage"
echo "  - Updated environment variables"
echo ""
read -p "Continue with deployment? (y/N): " confirm

if [[ $confirm != [yY] && $confirm != [yY][eE][sS] ]]; then
    echo -e "${YELLOW}Deployment cancelled${NC}"
    exit 0
fi

# Deploy to Vercel
echo -e "\n${BLUE}🚀 Deploying to Vercel...${NC}"
vercel --prod

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✅ Deployment successful!${NC}"
    echo -e "\n${BLUE}📝 Next steps:${NC}"
    echo "1. Set environment variables in Vercel dashboard:"
    echo "   - ENVIRONMENT=production"
    echo "   - PROD_DATABASE_URL=your_production_database_url"
    echo "   - PROD_BLOB_READ_WRITE_TOKEN=your_production_blob_token"
    echo "   - SECRET_KEY=your_secure_jwt_key"
    echo "   - ADMIN_EMAIL=your_admin_email"
    echo "   - ADMIN_PASSWORD=your_admin_password"
    echo ""
    echo "2. Test your deployment at the provided URL"
    echo "3. Monitor logs in Vercel dashboard"
else
    echo -e "\n${RED}❌ Deployment failed${NC}"
    echo "Check the error messages above and try again"
    exit 1
fi
