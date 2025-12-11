# tastelocal/models.py
"""
Shared models for TasteLocal platform.
These models are used across multiple apps.
"""

from django.db import models
from django.contrib.auth.models import User

class TimeStampedModel(models.Model):
    """Abstract base model with created and updated timestamps"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

class LocationModel(models.Model):
    """Abstract base model for location-based entities"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    address = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    class Meta:
        abstract = True