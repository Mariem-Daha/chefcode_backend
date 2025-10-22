@echo off
REM Git initialization and push script for ChefCode Backend

echo.
echo ================================================
echo   ChefCode Backend - Git Setup
echo ================================================
echo.

REM Check if git is installed
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Git is not installed or not in PATH
    echo Please install Git from: https://git-scm.com/download/win
    pause
    exit /b 1
)

REM Check if already initialized
if exist .git (
    echo [INFO] Git repository already initialized
    echo.
) else (
    echo [STEP 1] Initializing Git repository...
    git init
    echo [OK] Git repository initialized
    echo.
)

REM Show current status
echo [STEP 2] Current Git status:
echo.
git status --short
echo.

REM Add all files
echo [STEP 3] Adding all files to Git...
git add .
echo [OK] Files added
echo.

REM Commit
echo [STEP 4] Creating commit...
git commit -m "Prepare ChefCode backend for Render deployment"
if %errorlevel% equ 0 (
    echo [OK] Commit created
) else (
    echo [WARNING] Nothing to commit or commit failed
)
echo.

REM Check for remote
git remote -v >nul 2>&1
if %errorlevel% equ 0 (
    echo [INFO] Remote repository already configured:
    git remote -v
    echo.
    echo Ready to push? Enter 'y' to continue or 'n' to skip
    set /p push="Push to GitHub? (y/n): "
    if /i "%push%"=="y" (
        echo.
        echo [STEP 5] Pushing to GitHub...
        git push -u origin main
        if %errorlevel% equ 0 (
            echo [OK] Successfully pushed to GitHub!
        ) else (
            echo [ERROR] Push failed. You may need to set up the remote first.
            echo.
            echo Run these commands to add your GitHub repository:
            echo   git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git
            echo   git branch -M main
            echo   git push -u origin main
        )
    )
) else (
    echo [INFO] No remote repository configured
    echo.
    echo To push to GitHub, you need to:
    echo 1. Create a new repository on GitHub
    echo 2. Run these commands:
    echo.
    echo    git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git
    echo    git branch -M main
    echo    git push -u origin main
    echo.
)

echo.
echo ================================================
echo   Next Steps
echo ================================================
echo.
echo 1. [DONE] Git repository ready
echo 2. [TODO] Create GitHub repository (if not done)
echo 3. [TODO] Push to GitHub (if not done)
echo 4. [TODO] Deploy on Render
echo.
echo See RENDER_QUICK_START.md for deployment instructions
echo.
pause
