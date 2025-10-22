@echo off
REM Pre-deployment checklist script for Render (Windows)

echo.
echo ================================================
echo   ChefCode Backend - Render Deployment Checklist
echo ================================================
echo.

REM Check if git is initialized
echo [Checking Git repository...]
if exist .git (
    echo   [OK] Git repository found
) else (
    echo   [X] Git repository not initialized
    echo       Run: git init
)
echo.

REM Check required files
echo [Checking required files...]
set "missing=0"

if exist render.yaml (
    echo   [OK] render.yaml
) else (
    echo   [X] render.yaml ^(missing^)
    set "missing=1"
)

if exist build.sh (
    echo   [OK] build.sh
) else (
    echo   [X] build.sh ^(missing^)
    set "missing=1"
)

if exist requirements.txt (
    echo   [OK] requirements.txt
) else (
    echo   [X] requirements.txt ^(missing^)
    set "missing=1"
)

if exist main.py (
    echo   [OK] main.py
) else (
    echo   [X] main.py ^(missing^)
    set "missing=1"
)

if exist database.py (
    echo   [OK] database.py
) else (
    echo   [X] database.py ^(missing^)
    set "missing=1"
)

if exist .gitignore (
    echo   [OK] .gitignore
) else (
    echo   [X] .gitignore ^(missing^)
    set "missing=1"
)
echo.

REM Check if .env exists (should not be committed)
echo [Checking sensitive files...]
if exist .env (
    echo   [!] .env file exists ^(make sure it's in .gitignore^)
) else (
    echo   [OK] No .env file ^(good - use environment variables in Render^)
)
echo.

REM Check Python dependencies
echo [Checking Python dependencies...]
findstr /C:"psycopg2-binary" requirements.txt >nul 2>&1
if %errorlevel%==0 (
    echo   [OK] PostgreSQL support ^(psycopg2-binary^) found
) else (
    echo   [X] PostgreSQL support missing
    echo       Add to requirements.txt: psycopg2-binary==2.9.9
)

findstr /C:"fastapi" requirements.txt >nul 2>&1
if %errorlevel%==0 (
    echo   [OK] FastAPI found
) else (
    echo   [X] FastAPI missing
)

findstr /C:"uvicorn" requirements.txt >nul 2>&1
if %errorlevel%==0 (
    echo   [OK] Uvicorn found
) else (
    echo   [X] Uvicorn missing
)
echo.

REM Summary
echo ================================================
echo   Pre-Deployment Summary
echo ================================================
echo.
echo Next steps:
echo.
echo 1. Fix any [X] items above
echo.
echo 2. Commit and push to GitHub:
echo    git add .
echo    git commit -m "Prepare for Render deployment"
echo    git push origin main
echo.
echo 3. Deploy on Render:
echo    https://dashboard.render.com/blueprints
echo.
echo 4. Set environment variables in Render:
echo    - ENVIRONMENT=production
echo    - OPENAI_API_KEY=your_key_here
echo    - GEMINI_API_KEY=your_key_here
echo    - ALLOWED_ORIGINS=*
echo.
echo See RENDER_QUICK_START.md for detailed instructions
echo.
pause
