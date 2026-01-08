"""
Performance testing script for Simple LMS
Tests Redis caching and query optimization
"""

import time
import requests
from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.db import connection
from django.test.utils import override_settings
from lms.models import Course, User


class Command(BaseCommand):
    help = 'Run performance tests for LMS'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(self.style.SUCCESS('Simple LMS Performance Test'))
        self.stdout.write(self.style.SUCCESS('=' * 50))
        
        # Test 1: Database query performance
        self.test_database_queries()
        
        # Test 2: Redis cache performance
        self.test_redis_cache()
        
        # Test 3: API response time
        self.test_api_performance()
        
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 50))
        self.stdout.write(self.style.SUCCESS('Performance tests completed!'))
        self.stdout.write(self.style.SUCCESS('=' * 50))
    
    def test_database_queries(self):
        """Test database query performance"""
        self.stdout.write('\n--- Database Query Performance ---')
        
        # Reset query counter
        connection.queries_log.clear()
        
        # Test without optimization
        start = time.time()
        courses = Course.objects.all()
        for course in courses:
            _ = course.instructor.username
            _ = course.enrollments.count()
        queries_without_optimization = len(connection.queries)
        time_without = time.time() - start
        
        # Reset query counter
        connection.queries_log.clear()
        
        # Test with optimization
        start = time.time()
        courses = Course.objects.select_related('instructor').prefetch_related('enrollments')
        for course in courses:
            _ = course.instructor.username
            _ = course.enrollments.count()
        queries_with_optimization = len(connection.queries)
        time_with = time.time() - start
        
        self.stdout.write(f'\nWithout optimization:')
        self.stdout.write(f'  Queries: {queries_without_optimization}')
        self.stdout.write(f'  Time: {time_without:.4f}s')
        
        self.stdout.write(f'\nWith optimization:')
        self.stdout.write(f'  Queries: {queries_with_optimization}')
        self.stdout.write(f'  Time: {time_with:.4f}s')
        
        improvement = ((queries_without_optimization - queries_with_optimization) / queries_without_optimization) * 100
        self.stdout.write(self.style.SUCCESS(f'\n✓ Query reduction: {improvement:.1f}%'))
    
    def test_redis_cache(self):
        """Test Redis cache performance"""
        self.stdout.write('\n\n--- Redis Cache Performance ---')
        
        # Clear cache
        cache.clear()
        
        # Test cache miss (first request)
        start = time.time()
        cache.set('test_key', 'test_value', 300)
        time_set = time.time() - start
        
        # Test cache hit
        start = time.time()
        value = cache.get('test_key')
        time_get = time.time() - start
        
        self.stdout.write(f'\nCache SET time: {time_set:.6f}s')
        self.stdout.write(f'Cache GET time: {time_get:.6f}s')
        
        if value == 'test_value':
            self.stdout.write(self.style.SUCCESS('✓ Redis cache working correctly'))
        else:
            self.stdout.write(self.style.ERROR('✗ Redis cache not working'))
        
        # Test cache vs database
        cache_key = 'courses_test'
        
        # First request (cache miss)
        cache.delete(cache_key)
        start = time.time()
        courses = list(Course.objects.all())
        cache.set(cache_key, courses, 300)
        time_db = time.time() - start
        
        # Second request (cache hit)
        start = time.time()
        cached_courses = cache.get(cache_key)
        time_cache = time.time() - start
        
        self.stdout.write(f'\nDatabase query time: {time_db:.6f}s')
        self.stdout.write(f'Cache retrieval time: {time_cache:.6f}s')
        
        speedup = (time_db / time_cache) if time_cache > 0 else 0
        self.stdout.write(self.style.SUCCESS(f'✓ Cache is {speedup:.1f}x faster'))
    
    def test_api_performance(self):
        """Test API endpoint performance"""
        self.stdout.write('\n\n--- API Performance ---')
        
        base_url = 'http://localhost:8000/api/lms'
        
        try:
            # Test health endpoint
            start = time.time()
            response = requests.get(f'{base_url}/health')
            time_health = time.time() - start
            
            if response.status_code == 200:
                self.stdout.write(f'\nHealth check: {time_health:.4f}s')
                self.stdout.write(self.style.SUCCESS('✓ API is responding'))
            else:
                self.stdout.write(self.style.ERROR('✗ API health check failed'))
            
            # Test courses endpoint (first call - cache miss)
            cache.delete_pattern('courses_*')
            start = time.time()
            response1 = requests.get(f'{base_url}/courses')
            time_first = time.time() - start
            
            # Test courses endpoint (second call - cache hit)
            start = time.time()
            response2 = requests.get(f'{base_url}/courses')
            time_second = time.time() - start
            
            self.stdout.write(f'\nCourses API (cache miss): {time_first:.4f}s')
            self.stdout.write(f'Courses API (cache hit): {time_second:.4f}s')
            
            if time_second < time_first:
                improvement = ((time_first - time_second) / time_first) * 100
                self.stdout.write(self.style.SUCCESS(f'✓ Cache improved response time by {improvement:.1f}%'))
            
        except requests.exceptions.ConnectionError:
            self.stdout.write(self.style.WARNING('⚠ Could not connect to API. Make sure server is running.'))
