# tours/models.py
"""
Models for tour operator dashboard app - tour-specific data
"""

from django.db import models
from django.conf import settings
from vendors.models import Vendor

class TourOperator(models.Model):
    """Tour operator model representing tour companies/guides"""
    
    # UPDATED User reference
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Operator Profile Picture
    operator_pic = models.ImageField(
        upload_to='tour_operator_pics/',
        null=True,
        blank=True,
        verbose_name="Operator Profile Picture",
        help_text="Profile picture for the tour operator/company"
    )
    
    # Singapore-specific licensing and certifications
    singapore_license_number = models.CharField(
        max_length=50, 
        blank=True,
        verbose_name="Singapore Tourism Board License Number",
        help_text="e.g., 12345 (STB license number)"
    )
    natas_member = models.BooleanField(
        default=False,
        verbose_name="NATAS Member",
        help_text="Member of National Association of Travel Agents Singapore"
    )
    natas_membership_number = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="NATAS Membership Number",
        help_text="If applicable"
    )
    has_insurance = models.BooleanField(
        default=False,
        verbose_name="Public Liability Insurance",
        help_text="Has valid public liability insurance"
    )
    
    # Contact information
    business_phone = models.CharField(max_length=20, blank=True)
    business_email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    
    # Business Development Services
    booking_tourists_small = models.BooleanField(
        default=False,
        verbose_name="Booking for Tourists (up to 10)",
        help_text="Accept bookings for small tourist groups (1-10 people)"
    )
    booking_tourists_medium = models.BooleanField(
        default=False,
        verbose_name="Booking for Tourists (11 to 30)",
        help_text="Accept bookings for medium tourist groups (11-30 people)"
    )
    catering_tourists = models.BooleanField(
        default=False,
        verbose_name="Catering for Tourists",
        help_text="Provide catering services for tourist groups"
    )
    kitchen_tour = models.BooleanField(
        default=False,
        verbose_name="Kitchen Tour",
        help_text="Offer behind-the-scenes kitchen tours"
    )
    chef_lessons = models.BooleanField(
        default=False,
        verbose_name="Chef's Lessons",
        help_text="Offer cooking classes and chef demonstrations"
    )
    
    # Verification status
    is_verified = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.company_name
    
    @property
    def license_display(self):
        """Display formatted license information"""
        parts = []
        if self.singapore_license_number:
            parts.append(f"STB License: {self.singapore_license_number}")
        if self.natas_member:
            natas_info = "NATAS Member"
            if self.natas_membership_number:
                natas_info += f" ({self.natas_membership_number})"
            parts.append(natas_info)
        if self.has_insurance:
            parts.append("Insured")
        return " • ".join(parts) if parts else "No certifications"
    
    @property
    def business_services(self):
        """Get list of active business services"""
        services = []
        if self.booking_tourists_small:
            services.append("Small Group Bookings (up to 10)")
        if self.booking_tourists_medium:
            services.append("Medium Group Bookings (11-30)")
        if self.catering_tourists:
            services.append("Tourist Catering")
        if self.kitchen_tour:
            services.append("Kitchen Tours")
        if self.chef_lessons:
            services.append("Chef's Lessons")
        return services
    
    @property
    def operator_pic_url(self):
        """Get operator picture URL or return default"""
        if self.operator_pic:
            return self.operator_pic.url
        return "/static/images/default-operator.jpg"
    
    @property
    def display_pic(self):
        """Display appropriate picture - operator_pic or default"""
        return self.operator_pic if self.operator_pic else None
    
    class Meta:
        verbose_name = "Tour Operator"
        verbose_name_plural = "Tour Operators"


class Tour(models.Model):
    """Tour model representing food tours and experiences"""
    
    TOUR_TYPES = [
        ('walking', 'Walking Food Tour'),
        ('vehicle', 'Vehicle-based Tour'),
        ('cooking', 'Cooking Class'),
        ('market', 'Market Tour'),
    ]
    
    # Core tour information
    tour_operator = models.ForeignKey(TourOperator, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    tour_type = models.CharField(max_length=20, choices=TOUR_TYPES)
    description = models.TextField()
    
    # Tour Picture
    tour_pic = models.ImageField(
        upload_to='tour_pics/',
        null=True,
        blank=True,
        verbose_name="Tour Picture",
        help_text="Main picture for the tour"
    )
    
    # Tour details
    duration_minutes = models.IntegerField(help_text="Duration in minutes")
    max_participants = models.IntegerField(default=10)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    
    # Status and features
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    @property
    def tour_pic_url(self):
        """Get tour picture URL or return default"""
        if self.tour_pic:
            return self.tour_pic.url
        return "/static/images/default-tour.jpg"
    
    @property
    def display_pic(self):
        """Display appropriate picture - tour_pic or default"""
        return self.tour_pic if self.tour_pic else None
    
    @property
    def duration_hours(self):
        """Convert minutes to hours and minutes format"""
        hours = self.duration_minutes // 60
        minutes = self.duration_minutes % 60
        
        if hours == 0:
            return f"{minutes} minutes"
        elif minutes == 0:
            return f"{hours} hour{'s' if hours > 1 else ''}"
        else:
            return f"{hours} hour{'s' if hours > 1 else ''} {minutes} minutes"
    
    @property
    def price_display(self):
        """Format price with currency"""
        return f"${self.price:.2f}"
    
    @property
    def type_display(self):
        """Get display name for tour type"""
        return dict(self.TOUR_TYPES).get(self.tour_type, self.tour_type)
    
    @property
    def itinerary_count(self):
        """Count of itinerary items"""
        return self.itinerary.count()
    
    @property
    def has_itinerary(self):
        """Check if tour has itinerary items"""
        return self.itinerary.exists()
    
    def get_itinerary_with_vendors(self):
        """Get itinerary items with vendor information"""
        return self.itinerary.select_related('vendor').order_by('stop_order')
    
    @property
    def featured_vendors(self):
        """Get featured vendors from itinerary"""
        vendors = set()
        for item in self.itinerary.select_related('vendor').filter(vendor__is_featured=True):
            if item.vendor:
                vendors.add(item.vendor)
        return list(vendors)[:3]  # Return up to 3 featured vendors
    
    @property
    def cuisine_types(self):
        """Get all cuisine types from vendors in itinerary"""
        from vendors.models import CuisineType
        cuisine_ids = set()
        for item in self.itinerary.select_related('vendor').filter(vendor__isnull=False):
            if item.vendor:
                cuisine_ids.update(item.vendor.cuisine_types.values_list('id', flat=True))
        return CuisineType.objects.filter(id__in=cuisine_ids)
    
    @property
    def cuisine_display(self):
        """Display cuisine types as string"""
        cuisines = self.cuisine_types
        if cuisines:
            return ", ".join([c.name for c in cuisines])
        return "Various"
    
    class Meta:
        verbose_name = "Tour"
        verbose_name_plural = "Tours"
        ordering = ['-is_featured', 'name']


class TourItinerary(models.Model):
    """Itinerary items for tours - connects tours to vendors"""
    
    tour = models.ForeignKey('Tour', on_delete=models.CASCADE, related_name='itinerary')
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, null=True, blank=True)
    stop_order = models.IntegerField(help_text="Order of stop in the tour")
    duration_minutes = models.IntegerField(
        help_text="Time spent at this stop (optional)",
        null=True,
        blank=True
    )
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['stop_order']
        verbose_name = "Tour Itinerary"
        verbose_name_plural = "Tour Itineraries"
        unique_together = ['tour', 'stop_order']
    
    def __str__(self):
        vendor_name = self.vendor.business_name if self.vendor else "No vendor"
        return f"{self.stop_order}. {vendor_name}"
    
    @property
    def duration_display(self):
        """Display duration in minutes"""
        if self.duration_minutes:
            return f"{self.duration_minutes} minutes"
        return "Flexible"
    
    @property
    def vendor_name(self):
        """Get vendor name or placeholder"""
        return self.vendor.business_name if self.vendor else "Tour Stop"
    
    @property
    def vendor_type(self):
        """Get vendor type or None"""
        return self.vendor.vendor_type if self.vendor else None
    
    @property
    def vendor_cuisine(self):
        """Get vendor cuisine types"""
        if self.vendor:
            return self.vendor.get_cuisine_types_display()
        return ""
    
    @property
    def vendor_address(self):
        """Get vendor address"""
        return self.vendor.address if self.vendor else ""
    
    @property
    def vendor_image(self):
        """Get vendor image"""
        if self.vendor and self.vendor.business_pix:
            return self.vendor.business_pix.url
        return None
    
    def clean(self):
        """Validate stop order is unique for this tour"""
        from django.core.exceptions import ValidationError
        
        # Check for duplicate stop order for the same tour
        if TourItinerary.objects.filter(
            tour=self.tour, 
            stop_order=self.stop_order
        ).exclude(pk=self.pk).exists():
            raise ValidationError(f"Stop order {self.stop_order} already exists for this tour.")