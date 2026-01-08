"""
URL configuration for LMS app
"""

from django.urls import path
from .api import api

urlpatterns = [
    path('lms/', api.urls),
]
