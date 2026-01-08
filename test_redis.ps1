# Redis Cache Testing Guide

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Redis Cache Testing for Simple LMS" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Test 1: Redis Cache
Write-Host "TEST 1: Redis Cache" -ForegroundColor Yellow
Write-Host "Purpose: Verify that courses are cached in Redis" -ForegroundColor White
Write-Host ""
Write-Host "Steps:" -ForegroundColor Green
Write-Host "1. Open a new terminal and run: redis-cli monitor" -ForegroundColor White
Write-Host "2. Make a request to: http://localhost:8000/api/lms/courses" -ForegroundColor White
Write-Host "3. Check Redis monitor output for:" -ForegroundColor White
Write-Host "   - First request: SET lms:courses_list..." -ForegroundColor Gray
Write-Host "   - Second request: GET lms:courses_list" -ForegroundColor Gray
Write-Host ""

$test1 = Read-Host "Press Enter to make the first request (or 'skip' to skip)"
if ($test1 -ne "skip") {
    Write-Host "Making first request (cache miss)..." -ForegroundColor Yellow
    $response1 = Invoke-WebRequest -Uri "http://localhost:8000/api/lms/courses" -UseBasicParsing
    Write-Host "Response code: $($response1.StatusCode)" -ForegroundColor Green
    Start-Sleep -Seconds 2
    
    Write-Host "Making second request (cache hit)..." -ForegroundColor Yellow
    $response2 = Invoke-WebRequest -Uri "http://localhost:8000/api/lms/courses" -UseBasicParsing
    Write-Host "Response code: $($response2.StatusCode)" -ForegroundColor Green
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Test 2: Redis Session
Write-Host "TEST 2: Redis Session" -ForegroundColor Yellow
Write-Host "Purpose: Verify that Django sessions are stored in Redis" -ForegroundColor White
Write-Host ""
Write-Host "Steps:" -ForegroundColor Green
Write-Host "1. Make request to test-session endpoint" -ForegroundColor White
Write-Host "2. Check Redis for session keys" -ForegroundColor White
Write-Host ""

$test2 = Read-Host "Press Enter to test sessions (or 'skip' to skip)"
if ($test2 -ne "skip") {
    Write-Host "Creating session..." -ForegroundColor Yellow
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/lms/test-session" -UseBasicParsing -SessionVariable session
    Write-Host "Response: $($response.Content)" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "Now run these commands in redis-cli:" -ForegroundColor Yellow
    Write-Host "  select 1" -ForegroundColor Gray
    Write-Host "  keys `"*`"" -ForegroundColor Gray
    Write-Host "  (You should see session keys)" -ForegroundColor Gray
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Test 3: Cache Invalidation
Write-Host "TEST 3: Cache Invalidation" -ForegroundColor Yellow
Write-Host "Purpose: Verify cache is cleared when data changes" -ForegroundColor White
Write-Host ""
Write-Host "Steps:" -ForegroundColor Green
Write-Host "1. Get courses (creates cache)" -ForegroundColor White
Write-Host "2. Login and create new course" -ForegroundColor White
Write-Host "3. Watch Redis monitor for DEL command" -ForegroundColor White
Write-Host ""

$test3 = Read-Host "Press Enter to test cache invalidation (or 'skip' to skip)"
if ($test3 -ne "skip") {
    Write-Host "Getting courses..." -ForegroundColor Yellow
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/lms/courses" -UseBasicParsing
    Write-Host "Cache created" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "To complete this test:" -ForegroundColor Yellow
    Write-Host "1. Login as dosen: POST http://localhost:8000/api/lms/auth/login" -ForegroundColor White
    Write-Host "   Body: {`"email`": `"dosen1@lms.com`", `"password`": `"dosen123`"}" -ForegroundColor Gray
    Write-Host "2. Create course: POST http://localhost:8000/api/lms/courses" -ForegroundColor White
    Write-Host "   Headers: Authorization: Bearer <token>" -ForegroundColor Gray
    Write-Host "   Body: {`"title`":`"Test`",`"slug`":`"test`",`"description`":`"Test`",`"category`":`"Test`",`"level`":`"beginner`"}" -ForegroundColor Gray
    Write-Host "3. Watch Redis monitor for DEL lms:courses_list*" -ForegroundColor White
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Testing Complete!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "For detailed performance testing, run:" -ForegroundColor Yellow
Write-Host "  python manage.py performance_test" -ForegroundColor White
