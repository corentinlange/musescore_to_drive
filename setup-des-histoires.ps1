# Setup script for des-histoires repo
# Run this from c:\Users\coren\dev

Write-Host "🎵 Setting up des-histoires repo..." -ForegroundColor Cyan

# Navigate to parent directory
Set-Location "c:\Users\coren\dev"

# Clone the new repo
Write-Host "`n1. Cloning des-histoires..." -ForegroundColor Yellow
git clone https://github.com/corentinlange/des-histoires.git

# Enter the directory
Set-Location "des-histoires"

# Add upstream remote
Write-Host "`n2. Adding upstream remote..." -ForegroundColor Yellow
git remote add upstream https://github.com/corentinlange/musescore_to_drive.git

# Pull from original
Write-Host "`n3. Pulling from musescore_to_drive..." -ForegroundColor Yellow
git pull upstream main

# Push to new repo
Write-Host "`n4. Pushing to des-histoires..." -ForegroundColor Yellow
git push origin main

Write-Host "`n✅ Setup complete!" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. Add your .mscz files to this repo"
Write-Host "2. Configure GitHub secrets:"
Write-Host "   - GCP_SERVICE_ACCOUNT_KEY_B64"
Write-Host "   - DRIVE_FOLDER_ID"
Write-Host "`nTo sync updates later:"
Write-Host "  git pull upstream main"
Write-Host "  git push origin main"
