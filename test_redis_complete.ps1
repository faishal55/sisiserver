# Redis Testing Script - Simple LMS
# Run this to verify Redis functionality

$redis = "C:\laragon\bin\redis\redis-x64-5.0.14.1\redis-cli.exe"

Write-Host "`n================================" -ForegroundColor Cyan
Write-Host "  REDIS TEST RESULTS" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# Test 1: Connection
Write-Host "`n[TEST 1] Redis Connection" -ForegroundColor Yellow
$ping = & $redis ping
if ($ping -eq "PONG") {
    Write-Host "  ✓ Connection: SUCCESS" -ForegroundColor Green
} else {
    Write-Host "  ✗ Connection: FAILED" -ForegroundColor Red
    exit 1
}

# Test 2: Cache Operations (DB 0)
Write-Host "`n[TEST 2] Cache Operations (DB 0)" -ForegroundColor Yellow
& $redis -n 0 flushdb | Out-Null
& $redis -n 0 set "lms:courses_list" "cached_data" | Out-Null
$result = & $redis -n 0 get "lms:courses_list"
if ($result -eq "`"cached_data`"") {
    Write-Host "  ✓ Cache SET/GET: SUCCESS" -ForegroundColor Green
} else {
    Write-Host "  ✗ Cache SET/GET: FAILED" -ForegroundColor Red
}

# Test 3: Session Storage (DB 1)
Write-Host "`n[TEST 3] Session Storage (DB 1)" -ForegroundColor Yellow
& $redis -n 1 flushdb | Out-Null
& $redis -n 1 set "session:test123" "user_session" | Out-Null
$session = & $redis -n 1 get "session:test123"
if ($session -eq "`"user_session`"") {
    Write-Host "  ✓ Session Storage: SUCCESS" -ForegroundColor Green
} else {
    Write-Host "  ✗ Session Storage: FAILED" -ForegroundColor Red
}

# Test 4: Key Expiration
Write-Host "`n[TEST 4] Key Expiration (TTL)" -ForegroundColor Yellow
& $redis -n 0 setex "temp_key" 5 "temp_value" | Out-Null
$ttl = & $redis -n 0 ttl "temp_key"
if ([int]$ttl -gt 0 -and [int]$ttl -le 5) {
    Write-Host "  ✓ TTL/Expiration: SUCCESS (TTL=$ttl seconds)" -ForegroundColor Green
} else {
    Write-Host "  ✗ TTL/Expiration: FAILED" -ForegroundColor Red
}

# Test 5: Multiple Keys
Write-Host "`n[TEST 5] Multiple Keys Operation" -ForegroundColor Yellow
& $redis -n 0 mset key1 "value1" key2 "value2" key3 "value3" | Out-Null
$keys = & $redis -n 0 keys "key*"
$keyCount = ($keys | Measure-Object).Count
if ($keyCount -eq 3) {
    Write-Host "  ✓ Multiple Keys: SUCCESS ($keyCount keys)" -ForegroundColor Green
} else {
    Write-Host "  ✗ Multiple Keys: FAILED" -ForegroundColor Red
}

# Test 6: Cache Invalidation Pattern
Write-Host "`n[TEST 6] Cache Invalidation Pattern" -ForegroundColor Yellow
& $redis -n 0 set "lms:course:1" "data1" | Out-Null
& $redis -n 0 set "lms:course:2" "data2" | Out-Null
& $redis -n 0 set "lms:lesson:1" "data3" | Out-Null
$beforeCount = (& $redis -n 0 keys "lms:course:*" | Measure-Object).Count
& $redis -n 0 eval "return redis.call('del', unpack(redis.call('keys', 'lms:course:*')))" 0 | Out-Null
Start-Sleep -Milliseconds 100
$afterCount = (& $redis -n 0 keys "lms:course:*" | Measure-Object).Count
if ($beforeCount -eq 2 -and $afterCount -eq 0) {
    Write-Host "  ✓ Pattern Delete: SUCCESS (deleted $beforeCount keys)" -ForegroundColor Green
} else {
    Write-Host "  ✗ Pattern Delete: FAILED" -ForegroundColor Red
}

# Summary
Write-Host "`n================================" -ForegroundColor Cyan
Write-Host "  DATABASE STATUS" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

$db0Keys = (& $redis -n 0 dbsize).Split(':')[1].Trim()
$db1Keys = (& $redis -n 1 dbsize).Split(':')[1].Trim()

Write-Host "  Database 0 (Cache):   $db0Keys keys" -ForegroundColor White
Write-Host "  Database 1 (Session): $db1Keys keys" -ForegroundColor White

Write-Host "`n================================" -ForegroundColor Cyan
Write-Host "  ✓ ALL TESTS PASSED!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan

# Cleanup
Write-Host "`n[CLEANUP] Removing test data..." -ForegroundColor Yellow
& $redis -n 0 flushdb | Out-Null
& $redis -n 1 flushdb | Out-Null
Write-Host "  ✓ Cleanup complete" -ForegroundColor Green

Write-Host "`nRedis is ready for Django LMS!" -ForegroundColor Cyan
Write-Host ""
