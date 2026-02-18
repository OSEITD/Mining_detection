@echo off
echo ============================================================
echo GITHUB ACTIONS SETUP FOR GEE AUTOMATION
echo ============================================================
echo.

REM Check if git is initialized
if not exist ".git" (
    echo Initializing Git repository...
    git init
    git branch -M main
    echo.
)

REM Check if files exist
if not exist "gee_automation\github_actions_gee.py" (
    echo ERROR: Required files not found
    echo Please run this from the Project root directory
    pause
    exit /b 1
)

echo Step 1: Checking Git status...
echo.
git status
echo.

echo ============================================================
echo Step 2: REQUIRED - Set up GitHub Secrets
echo ============================================================
echo.
echo You need to add these secrets to your GitHub repository:
echo.
echo 1. Go to: https://github.com/YOUR_USERNAME/YOUR_REPO/settings/secrets/actions
echo.
echo 2. Click "New repository secret" and add:
echo.
echo    Name: SUPABASE_URL
echo    Value: https://ntkzaobvbsppxbljamvb.supabase.co
echo.
echo    Name: SUPABASE_KEY  
echo    Value: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im50a3phb2J2YnNwcHhibGphbXZiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIzNzM2MDAsImV4cCI6MjA3Nzk0OTYwMH0.Tq3N_1Kta0eGZOQiFolcyS5L3NjTAlgHBqUlq5-cqxw
echo.
echo 3. For Earth Engine authentication:
echo.
echo    Option A - Personal Auth (Easier):
echo    Run: earthengine authenticate
echo    Then add the credentials file content as:
echo    Name: EARTHENGINE_TOKEN
echo    Value: (content from C:\Users\%USERNAME%\.config\earthengine\credentials)
echo.
echo    Option B - Service Account (Production):
echo    Create service account at: https://console.cloud.google.com
echo    Name: GEE_SERVICE_ACCOUNT_KEY
echo    Value: (entire JSON key file content)
echo.
echo ============================================================
echo.

set /p READY="Have you added the secrets to GitHub? (y/n): "
if /i not "%READY%"=="y" (
    echo.
    echo Please add the secrets first, then run this script again.
    pause
    exit /b 0
)

echo.
echo ============================================================
echo Step 3: Committing files...
echo ============================================================
echo.

git add .github/workflows/gee_automation.yml
git add gee_automation/
git add *.md

git commit -m "Add GitHub Actions for GEE automation"

echo.
echo ============================================================
echo Step 4: Push to GitHub
echo ============================================================
echo.

set /p REPO_URL="Enter your GitHub repository URL (https://github.com/username/repo.git): "

if "%REPO_URL%"=="" (
    echo No URL provided. Please push manually:
    echo   git remote add origin YOUR_REPO_URL
    echo   git push -u origin main
    pause
    exit /b 0
)

REM Check if remote exists
git remote | findstr "origin" >nul
if errorlevel 1 (
    echo Adding remote origin...
    git remote add origin %REPO_URL%
)

echo Pushing to GitHub...
git push -u origin main

echo.
echo ============================================================
echo Step 5: Enable GitHub Actions
echo ============================================================
echo.
echo 1. Go to your repository on GitHub
echo 2. Click the "Actions" tab
echo 3. If prompted, click "I understand my workflows, go ahead and enable them"
echo 4. You should see "Automated Satellite Data Collection" workflow
echo 5. Click "Run workflow" to test it manually
echo.

echo ============================================================
echo ✅ SETUP COMPLETE!
echo ============================================================
echo.
echo Your automated GEE workflow is ready!
echo.
echo Next steps:
echo   1. Go to: https://github.com/%REPO_URL:~19,-4%/actions
echo   2. Click "Automated Satellite Data Collection"
echo   3. Click "Run workflow" to test
echo   4. Check Supabase for new satellite_updates record
echo.
echo The workflow will run automatically every 5 days at 2 AM UTC.
echo.

pause
