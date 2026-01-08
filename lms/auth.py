"""
JWT Authentication utilities for Simple LMS
"""

import jwt
from datetime import datetime, timedelta
from typing import Optional
from django.conf import settings
from django.contrib.auth import get_user_model
from functools import wraps
from ninja.security import HttpBearer

User = get_user_model()


def create_jwt_token(user) -> str:
    """
    Create JWT token for user
    
    Args:
        user: User instance
        
    Returns:
        JWT token string
    """
    payload = {
        'user_id': user.id,
        'email': user.email,
        'username': user.username,
        'role': user.role,
        'exp': datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRATION_HOURS),
        'iat': datetime.utcnow(),
    }
    
    token = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    
    return token


def decode_jwt_token(token: str) -> Optional[dict]:
    """
    Decode JWT token
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded payload or None if invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


class JWTAuth(HttpBearer):
    """JWT Authentication for Django Ninja"""
    
    def authenticate(self, request, token):
        """
        Authenticate request using JWT token
        
        Args:
            request: HTTP request
            token: JWT token from Authorization header
            
        Returns:
            User instance or None
        """
        payload = decode_jwt_token(token)
        if not payload:
            return None
        
        try:
            user = User.objects.get(id=payload['user_id'], is_active=True)
            return user
        except User.DoesNotExist:
            return None


def require_role(*allowed_roles):
    """
    Decorator to require specific user roles
    
    Usage:
        @require_role('admin', 'dosen')
        def my_view(request):
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            user = request.auth
            
            if not user:
                from ninja.errors import HttpError
                raise HttpError(401, "Authentication required")
            
            if user.role not in allowed_roles:
                from ninja.errors import HttpError
                raise HttpError(403, "Permission denied")
            
            return func(request, *args, **kwargs)
        return wrapper
    return decorator


def get_user_from_token(token: str) -> Optional[User]:
    """
    Get user from JWT token
    
    Args:
        token: JWT token string
        
    Returns:
        User instance or None
    """
    payload = decode_jwt_token(token)
    if not payload:
        return None
    
    try:
        return User.objects.get(id=payload['user_id'], is_active=True)
    except User.DoesNotExist:
        return None
