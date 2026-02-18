# Quick ngrok Setup Script
# Run this AFTER you've downloaded and extracted ngrok

Write-Host "=== ngrok Quick Setup ===" -ForegroundColor Cyan
Write-Host ""

# Ask where ngrok was extracted
Write-Host "Where did you extract ngrok?" -ForegroundColor Yellow
Write-Host "1. Downloads folder (default)"
Write-Host "2. C:\ngrok"
Write-Host "3. Other location"
Write-Host ""

$choice = Read-Host "Enter choice (1-3)"

switch ($choice) {
    "1" { 
        $ngrokPath = "$env:USERPROFILE\Downloads\ngrok"
    }
    "2" { 
        $ngrokPath = "C:\ngrok"
    }
    "3" { 
        $ngrokPath = Read-Host "Enter full path to ngrok folder"
    }
    default { 
        $ngrokPath = "$env:USERPROFILE\Downloads\ngrok"
    }
}

Write-Host ""
Write-Host "Using ngrok path: $ngrokPath" -ForegroundColor Green

if (Test-Path "$ngrokPath\ngrok.exe") {
    Write-Host "✓ ngrok.exe found!" -ForegroundColor Green
    
    # Add authtoken
    Write-Host ""
    Write-Host "Adding authtoken..." -ForegroundColor Cyan
    & "$ngrokPath\ngrok.exe" config add-authtoken 35370A3pC8t3l7gl4UE5G5sEN8G_4MxwRSycu6iJUmgikq5gx
    
    Write-Host ""
    Write-Host "✓ Setup complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Make sure Streamlit is running on port 8511"
    Write-Host "2. Run this command in a NEW PowerShell window:"
    Write-Host ""
    Write-Host "   cd `"$ngrokPath`"" -ForegroundColor White
    Write-Host "   .\ngrok http 8511" -ForegroundColor White
    Write-Host ""
    Write-Host "3. Copy the HTTPS URL and open it in your browser"
    Write-Host "4. Click the Install icon in the address bar"
    Write-Host ""
    
    # Ask if user wants to start ngrok now
    $startNow = Read-Host "Start ngrok now? (y/n)"
    if ($startNow -eq "y") {
        Write-Host ""
        Write-Host "Starting ngrok..." -ForegroundColor Cyan
        Write-Host "Press Ctrl+C to stop when done" -ForegroundColor Yellow
        Write-Host ""
        Start-Sleep -Seconds 2
        & "$ngrokPath\ngrok.exe" http 8511
    }
    
} else {
    Write-Host "✗ ngrok.exe not found at: $ngrokPath" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please:" -ForegroundColor Yellow
    Write-Host "1. Download ngrok from: https://ngrok.com/download"
    Write-Host "2. Extract the ZIP file"
    Write-Host "3. Run this script again"
    Write-Host ""
    
    # Open download page
    $openPage = Read-Host "Open download page now? (y/n)"
    if ($openPage -eq "y") {
        Start-Process "https://ngrok.com/download"
    }
}
