"""
Cache utilities and helpers for Simple LMS
"""

from django.core.cache import cache
from functools import wraps
import hashlib
import json


def cache_key_builder(*args, **kwargs):
    """
    Build a cache key from arguments
    
    Example:
        cache_key_builder('courses', 'list', category='programming')
        -> 'courses:list:category=programming'
    """
    parts = [str(arg) for arg in args]
    
    if kwargs:
        sorted_kwargs = sorted(kwargs.items())
        kwargs_str = ':'.join([f"{k}={v}" for k, v in sorted_kwargs if v is not None])
        if kwargs_str:
            parts.append(kwargs_str)
    
    return ':'.join(parts)


def cache_response(timeout=300, key_prefix=''):
    """
    Decorator to cache function results
    
    Usage:
        @cache_response(timeout=600, key_prefix='user')
        def get_user_data(user_id):
            return User.objects.get(id=user_id)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Build cache key
            cache_key = cache_key_builder(
                key_prefix or func.__name__,
                *args,
                **kwargs
            )
            
            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Call function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout)
            
            return result
        return wrapper
    return decorator


def invalidate_cache_pattern(pattern):
    """
    Invalidate all cache keys matching a pattern
    
    Example:
        invalidate_cache_pattern('courses:*')
    """
    cache.delete_pattern(pattern)


def invalidate_model_cache(model_name):
    """
    Invalidate all cache related to a model
    
    Example:
        invalidate_model_cache('course')
    """
    patterns = [
        f"{model_name}:*",
        f"*:{model_name}:*",
        f"{model_name}s:*",  # plural
    ]
    
    for pattern in patterns:
        cache.delete_pattern(pattern)


def get_or_set_cache(key, callback, timeout=300):
    """
    Get value from cache or set it using callback
    
    Example:
        def expensive_query():
            return Course.objects.all()
        
        courses = get_or_set_cache('courses:all', expensive_query, 600)
    """
    value = cache.get(key)
    
    if value is None:
        value = callback()
        cache.set(key, value, timeout)
    
    return value


def cache_model_instance(instance, timeout=300):
    """
    Cache a model instance by its primary key
    
    Example:
        cache_model_instance(course, timeout=600)
    """
    model_name = instance.__class__.__name__.lower()
    cache_key = f"{model_name}:{instance.pk}"
    cache.set(cache_key, instance, timeout)


def get_cached_model_instance(model_class, pk):
    """
    Get a cached model instance by primary key
    
    Example:
        course = get_cached_model_instance(Course, 1)
    """
    model_name = model_class.__name__.lower()
    cache_key = f"{model_name}:{pk}"
    
    instance = cache.get(cache_key)
    
    if instance is None:
        try:
            instance = model_class.objects.get(pk=pk)
            cache_model_instance(instance)
        except model_class.DoesNotExist:
            return None
    
    return instance


class CacheInvalidator:
    """
    Context manager for cache invalidation
    
    Usage:
        with CacheInvalidator('courses'):
            course.save()
    """
    
    def __init__(self, *patterns):
        self.patterns = patterns
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:  # Only invalidate if no exception
            for pattern in self.patterns:
                invalidate_cache_pattern(f"{pattern}*")


# Predefined cache timeouts
CACHE_TIMEOUT = {
    'short': 60,        # 1 minute
    'medium': 300,      # 5 minutes
    'long': 1800,       # 30 minutes
    'hour': 3600,       # 1 hour
    'day': 86400,       # 24 hours
}
