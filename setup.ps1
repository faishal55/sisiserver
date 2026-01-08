# Simple LMS Setup Script for Windows PowerShell

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Simple LMS Setup Script" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version
    Write-Host "✓ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found. Please install Python 3.11+" -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host "`nCreating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "Virtual environment already exists" -ForegroundColor Green
} else {
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "`nActivating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1
Write-Host "✓ Virtual environment activated" -ForegroundColor Green

# Install dependencies
Write-Host "`nInstalling dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt
Write-Host "✓ Dependencies installed" -ForegroundColor Green

# Copy .env file
Write-Host "`nSetting up environment variables..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host ".env file already exists" -ForegroundColor Green
} else {
    Copy-Item .env.example .env
    Write-Host "✓ .env file created. Please update with your configuration" -ForegroundColor Green
}

# Create logs directory
Write-Host "`nCreating logs directory..." -ForegroundColor Yellow
if (!(Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs"
    Write-Host "✓ Logs directory created" -ForegroundColor Green
} else {
    Write-Host "Logs directory already exists" -ForegroundColor Green
}

Write-Host "`n================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Make sure PostgreSQL is running" -ForegroundColor White
Write-Host "2. Make sure Redis is running" -ForegroundColor White
Write-Host "3. Update .env file with your database credentials" -ForegroundColor White
Write-Host "4. Run: python manage.py makemigrations" -ForegroundColor White
Write-Host "5. Run: python manage.py migrate" -ForegroundColor White
Write-Host "6. Run: python manage.py seed_data" -ForegroundColor White
Write-Host "7. Run: python manage.py runserver" -ForegroundColor White
Write-Host ""
Write-Host "Access the API at: http://localhost:8000/api/lms/docs" -ForegroundColor Cyan
Write-Host "Access Django Admin at: http://localhost:8000/admin" -ForegroundColor Cyan
