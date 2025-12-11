# vendors/admin.py
"""
Admin configuration for vendors app
"""

from django.contrib import admin
from django import forms
from django.core.exceptions import ValidationError
from .models import Vendor, MenuItem, CuisineType, Event

class VendorForm(forms.ModelForm):
    """Custom form for Vendor admin with user validation"""
    class Meta:
        model = Vendor
        fields = '__all__'
    
    def clean_user(self):
        user = self.cleaned_data.get('user')
        if user and hasattr(user, 'user_type') and user.user_type != 'vendor':
            raise ValidationError(
                f"Only users with user_type 'vendor' can be linked to Vendor profiles. "
                f"Selected user has user_type '{user.user_type}'."
            )
        return user

# Inline admin for MenuItems
class MenuItemInline(admin.TabularInline):
    model = MenuItem
    extra = 1
    fields = ['dish_name', 'dish_price', 'is_market_price', 'dish_pix', 'is_vegetarian', 'is_vegan']
    show_change_link = True

# Inline admin for Events (ALL VENDOR TYPES CAN CREATE EVENTS)
class EventInline(admin.TabularInline):
    model = Event
    extra = 1
    fields = ['event_name', 'event_start_date', 'event_end_date', 'event_address', 'is_active']
    show_change_link = True
    
    def get_queryset(self, request):
        return super().get_queryset(request)
    
    # REMOVED: vendor type restriction - any vendor can create events
    def has_add_permission(self, request, obj=None):
        return True  # All vendors can add events

class VendorAdmin(admin.ModelAdmin):
    form = VendorForm
    list_display = ['business_name', 'vendor_type','description_truncated', 'has_business_pix', 'user']
    list_filter = ['vendor_type', 'accept_tour_partnership', 'catering_service', 'is_verified', 'is_featured', 'is_active', 'created_at']
    search_fields = ['business_name', 'address', 'email', 'phone', 'user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['cuisine_types']
    
    # Limit user choices to only vendor users
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            # Only show users with user_type='vendor'
            from django.contrib.auth import get_user_model
            User = get_user_model()
            kwargs["queryset"] = User.objects.filter(user_type='vendor')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    # Dynamic inlines - ALL VENDOR TYPES CAN HAVE EVENTS
    def get_inlines(self, request, obj=None):
        inlines = [MenuItemInline]
        # Always show EventInline for all vendor types
        inlines.append(EventInline)
        return inlines
    
    # Dynamic fieldsets based on vendor type
    def get_fieldsets(self, request, obj=None):
        # Base fields for all vendors
        fieldsets = (
            ('Basic Information', {
                'fields': ('user', 'business_name', 'vendor_type', 'description', 'business_pix')
            }),
            ('Contact Information', {
                'fields': ('phone', 'email', 'website')
            }),
            ('Cuisine & Dietary Certifications', {
                'fields': ('cuisine_types', 'halal', 'kosher', 'vegetarian')  # ADDED: halal field
            }),
            ('Booking System', {
                'fields': ('booking_type', 'external_booking_link', 'reservation_instructions', 'max_group_size', 'advance_notice_hours'),
                'classes': ('collapse',)
            }),
            ('Status & Features', {
                'fields': ('is_verified', 'is_featured', 'is_active')
            }),
            ('Timestamps', {
                'fields': ('created_at', 'updated_at'),
                'classes': ('collapse',)
            }),
        )
        
        # Add location and hours fields for restaurants and stalls
        if not obj or obj.vendor_type in ['restaurant', 'stall']:
            fieldsets = fieldsets[:1] + (
                ('Location & Hours', {
                    'fields': ('address', 'latitude', 'longitude', 'opening_hours')
                }),
            ) + fieldsets[1:]
        
        return fieldsets
    
    def has_fixed_location(self, obj):
        """Display fixed location status"""
        return obj.has_fixed_location
    has_fixed_location.boolean = True
    has_fixed_location.short_description = 'Fixed Location'
    
    def description_truncated(self, obj):
        """Display truncated description"""
        if obj.description:
            return obj.description[:100] + "..." if len(obj.description) > 100 else obj.description
        return "No description"
    description_truncated.short_description = 'Description'
    
    def has_business_pix(self, obj):
        """Display if business picture has been added"""
        return bool(obj.business_pix)
    has_business_pix.boolean = True
    has_business_pix.short_description = 'Has Photo'

# Register all models at the end to avoid duplicate registration
admin.site.register(Vendor, VendorAdmin)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['event_name', 'vendor', 'vendor_type_display', 'event_type', 'event_start_date', 'event_end_date', 'is_current', 'is_active']
    list_filter = ['event_type', 'is_active', 'is_recurring', 'event_start_date', 'vendor', 'vendor__vendor_type', 'event_cuisine']
    search_fields = ['event_name', 'event_description', 'event_address', 'event_website', 'vendor__business_name']
    readonly_fields = ['created_at', 'updated_at', 'is_current', 'is_upcoming', 'is_past']
    date_hierarchy = 'event_start_date'
    filter_horizontal = ['event_cuisine']
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "vendor":
            kwargs["queryset"] = db_field.related_model.objects.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    fieldsets = (
        ('Event Information', {
            'fields': ('vendor', 'event_name', 'event_description', 'event_type', 'event_cuisine', 'event_website', 'event_pix')
        }),
        ('Event Timing', {
            'fields': ('event_start_date', 'event_start_time', 'event_end_date', 'event_end_time')
        }),
        ('Event Location', {
            'fields': ('event_address', 'event_latitude', 'event_longitude')
        }),
        ('Recurrence', {
            'fields': ('is_recurring', 'recurrence_pattern'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active',)  # Removed is_featured
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def is_current(self, obj):
        return obj.is_current
    is_current.boolean = True
    is_current.short_description = 'Currently Active'
    
    def vendor_type_display(self, obj):
        return obj.vendor.get_vendor_type_display() if obj.vendor else 'No vendor'
    vendor_type_display.short_description = 'Vendor Type'

@admin.register(CuisineType)
class CuisineTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']
    list_per_page = 20

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['dish_name', 'vendor', 'display_price', 'is_market_price', 'is_vegetarian']
    list_filter = ['is_market_price', 'is_vegetarian', 'is_vegan', 'vendor', 'vendor__vendor_type']
    search_fields = ['dish_name', 'dish_description', 'vendor__business_name']
    readonly_fields = ['created_at', 'updated_at']
    list_select_related = ['vendor']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('vendor', 'dish_name', 'dish_description', 'dish_pix')
        }),
        ('Pricing', {
            'fields': ('is_market_price', 'dish_price'),
            'description': 'Set either market pricing or fixed price'
        }),
        ('Dietary Information', {
            'fields': ('is_vegetarian', 'is_vegan')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def display_price(self, obj):
        return obj.display_price
    display_price.short_description = 'Price'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('vendor')