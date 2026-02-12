# PowerShell script to copy frontend files from UI Design folder

$source = "c:\Users\Ali Comuter\Downloads\Video Production UI Design"
$destination = "frontend"

Write-Host "Copying frontend files..." -ForegroundColor Green

# Copy all files and folders
Copy-Item -Path "$source\*" -Destination $destination -Recurse -Force

Write-Host "✅ Frontend files copied successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. cd frontend"
Write-Host "2. npm install"
Write-Host "3. Copy .env.example to .env and add your Firebase keys"
Write-Host "4. npm run dev"
