#!/usr/bin/env bash
# Pre-deployment checklist script for Render

echo "🔍 ChefCode Backend - Render Deployment Checklist"
echo "=================================================="
echo ""

# Check if git is initialized
echo "✓ Checking Git repository..."
if [ -d .git ]; then
    echo "  ✅ Git repository found"
else
    echo "  ❌ Git repository not initialized"
    echo "     Run: git init"
fi
echo ""

# Check required files
echo "✓ Checking required files..."
required_files=("render.yaml" "build.sh" "requirements.txt" "main.py" "database.py" ".gitignore")
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file (missing)"
    fi
done
echo ""

# Check if .env exists (should not be committed)
echo "✓ Checking sensitive files..."
if [ -f .env ]; then
    echo "  ⚠️  .env file exists (make sure it's in .gitignore)"
else
    echo "  ✅ No .env file (good - use environment variables in Render)"
fi
echo ""

# Check if build.sh is executable
echo "✓ Checking file permissions..."
if [ -x build.sh ]; then
    echo "  ✅ build.sh is executable"
else
    echo "  ❌ build.sh is not executable"
    echo "     Run: chmod +x build.sh"
fi
echo ""

# Check Python dependencies
echo "✓ Checking Python dependencies..."
if grep -q "psycopg2-binary" requirements.txt; then
    echo "  ✅ PostgreSQL support (psycopg2-binary) found"
else
    echo "  ❌ PostgreSQL support missing"
    echo "     Add to requirements.txt: psycopg2-binary==2.9.9"
fi

if grep -q "fastapi" requirements.txt; then
    echo "  ✅ FastAPI found"
else
    echo "  ❌ FastAPI missing"
fi

if grep -q "uvicorn" requirements.txt; then
    echo "  ✅ Uvicorn found"
else
    echo "  ❌ Uvicorn missing"
fi
echo ""

# Summary
echo "=================================================="
echo "📋 Pre-Deployment Summary"
echo "=================================================="
echo ""
echo "Next steps:"
echo "1. Fix any ❌ items above"
echo "2. Commit and push to GitHub:"
echo "   git add ."
echo "   git commit -m 'Prepare for Render deployment'"
echo "   git push origin main"
echo ""
echo "3. Deploy on Render:"
echo "   https://dashboard.render.com/blueprints"
echo ""
echo "4. Set environment variables in Render:"
echo "   - ENVIRONMENT=production"
echo "   - OPENAI_API_KEY=your_key_here"
echo "   - GEMINI_API_KEY=your_key_here"
echo "   - ALLOWED_ORIGINS=*"
echo ""
echo "📚 See RENDER_QUICK_START.md for detailed instructions"
echo ""
