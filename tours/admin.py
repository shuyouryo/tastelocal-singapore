# tours/admin.py
"""
Admin configuration for tours app
"""

from django.contrib import admin
from .models import TourOperator, Tour, TourItinerary

# Inline admin for TourItinerary
class TourItineraryInline(admin.TabularInline):
    """Inline admin for TourItinerary within Tour admin"""
    model = TourItinerary
    extra = 1
    fields = ['stop_order', 'duration_minutes', 'description', 'vendor']
    show_change_link = True

@admin.register(TourOperator)
class TourOperatorAdmin(admin.ModelAdmin):
    """Admin interface for TourOperator model"""
    list_display = ['company_name', 'user', 'is_verified']
    list_filter = ['is_verified']
    search_fields = ['company_name']

@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    """Admin interface for Tour model"""
    list_display = ['name', 'tour_operator', 'tour_type', 'price', 'is_active']
    list_filter = ['tour_type', 'is_active']
    search_fields = ['name', 'description']
    inlines = [TourItineraryInline]

@admin.register(TourItinerary)
class TourItineraryAdmin(admin.ModelAdmin):
    """Admin interface for TourItinerary model"""
    list_display = ['tour', 'vendor', 'stop_order', 'duration_minutes']
    list_filter = ['tour']
    search_fields = ['tour__name', 'vendor__business_name']