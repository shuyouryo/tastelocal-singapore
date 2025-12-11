# vendors/models.py
"""
Models for vendor dashboard app - vendor-specific data
"""

from django.db import models
from django.conf import settings
from django.utils import timezone


class Vendor(models.Model):
    VENDOR_TYPES = [
        ('restaurant', 'Restaurant'),
        ('stall', 'Food Stall'),
        ('event', 'Pop-up & Event'),
    ]
    
    BOOKING_TYPE_CHOICES = [
        ('walk_in', 'Walk-in Only - No Reservations'),
        ('call_reservation', 'Call to Reserve - Phone Booking'),
        ('online_reservation', 'Online Reservation System'),
        ('event_ticketing', 'Event Ticketing - External System'),
    ]
    
    # ===== CORE VENDOR INFORMATION (ALL VENDOR TYPES) =====
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    business_name = models.CharField(max_length=200)
    vendor_type = models.CharField(max_length=20, choices=VENDOR_TYPES)
    description = models.TextField(blank=True)
    
    # ===== CUISINE TYPES (ALL VENDOR TYPES) - MAKE NULLABLE =====
    cuisine_types = models.ManyToManyField(
        'CuisineType', 
        related_name='vendors',
        blank=True,  # Add this to make it optional
        help_text="Cuisine types served (leave blank for event organizers who don't cook)"
    )
    
    # ===== LOCATION DETAILS (RESTAURANTS & FOOD STALLS ONLY) =====
    address = models.TextField(
        null=True, 
        blank=True, 
        help_text="Fixed business address (for restaurants & food stalls only)"
    )
    latitude = models.DecimalField(
        max_digits=10, 
        decimal_places=8, 
        null=True, 
        blank=True, 
        help_text="Fixed location latitude (for restaurants & food stalls only)"
    )
    longitude = models.DecimalField(
        max_digits=11, 
        decimal_places=8, 
        null=True, 
        blank=True, 
        help_text="Fixed location longitude (for restaurants & food stalls only)"
    )
    
    # ===== OPENING HOURS (RESTAURANTS & FOOD STALLS ONLY) =====
    opening_hours = models.TextField(
        blank=True, 
        help_text="Regular opening hours (for restaurants & food stalls only)"
    )
    
    # ===== CONTACT INFORMATION (ALL VENDOR TYPES) =====
    phone = models.CharField(
        max_length=20, 
        blank=True,
        help_text="Primary contact number for reservations and inquiries"
    )
    email = models.EmailField(
        blank=True, 
        max_length=254,
        help_text="Primary contact email"
    )
    website = models.URLField(
        blank=True, 
        max_length=200,
        help_text="Business website URL"
    )
    
    # ===== DIETARY CERTIFICATIONS (ALL VENDOR TYPES) =====
    halal = models.BooleanField(default=False)
    kosher = models.BooleanField(default=False)
    vegetarian = models.BooleanField(default=False)
    
    # ===== NEW BUSINESS SERVICES =====
    accept_tour_partnership = models.BooleanField(
        default=False,
        verbose_name="Accepts Tour Partnerships",
        help_text="Check if this vendor is open to partnering with food tours"
    )
    
    catering_service = models.BooleanField(
        default=False,
        verbose_name="Catering Service Available",
        help_text="Check if this vendor offers catering services"
    )
    
    # ===== RESERVATION & BOOKING SYSTEM =====
    booking_type = models.CharField(
        max_length=20,
        choices=BOOKING_TYPE_CHOICES,
        default='walk_in',
        help_text="How customers can book this vendor"
    )
    external_booking_link = models.TextField(
        blank=True,
        verbose_name="Booking System URL(s)",
        help_text="URL(s) for reservations or ticketing system. Multiple URLs can be separated by commas or new lines."
    )
    reservation_instructions = models.TextField(
        blank=True,
        help_text="Specific instructions for making reservations"
    )
    max_group_size = models.PositiveIntegerField(
        default=0,
        help_text="Maximum group size allowed (0 = no limit)"
    )
    advance_notice_hours = models.PositiveIntegerField(
        default=24,
        help_text="Required advance notice for bookings in hours"
    )
    
    # ===== BUSINESS IMAGE (ALL VENDOR TYPES) =====
    business_pix = models.ImageField(upload_to='vendor_business_pix/', null=True, blank=True)
    
    # ===== STATUS AND FEATURES (ALL VENDOR TYPES) =====
    is_verified = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # ===== TIMESTAMPS (ALL VENDOR TYPES) =====
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.business_name
    
    def get_cuisine_types_display(self):
        """Safe display method that handles empty cuisine types"""
        cuisines = self.cuisine_types.all()
        if cuisines:
            return ", ".join([cuisine.name for cuisine in cuisines])
        return "Not specified"
    
    @property
    def has_cuisine_types(self):
        """Check if vendor has cuisine types specified"""
        return self.cuisine_types.exists()
    
    @property
    def is_food_preparer(self):
        """Check if this vendor actually prepares food (restaurants, food stalls)"""
        return self.vendor_type in ['restaurant', 'stall']
    
    @property
    def is_event_organizer(self):
        """Check if this vendor is an event organizer (venue provider)"""
        return self.vendor_type == 'event'
    
    @property
    def has_fixed_location(self):
        """Check if vendor has a fixed physical location (restaurants & food stalls only)"""
        return bool(self.vendor_type in ['restaurant', 'stall'] and self.address and self.address.strip())
    
    @property
    def booking_link_label(self):
        """Get the appropriate label for the booking link based on type"""
        if self.booking_type == 'online_reservation':
            return "Make Reservation"
        elif self.booking_type == 'event_ticketing':
            return "Get Tickets"
        return "Book Now"
    
    @property
    def booking_system_name(self):
        """Get descriptive name of the booking system"""
        if self.booking_type == 'online_reservation':
            return "Online Reservation System"
        elif self.booking_type == 'event_ticketing':
            return "Ticketing System"
        return "Booking System"
    
    @property
    def requires_external_link(self):
        """Check if this booking type needs an external link"""
        return self.booking_type in ['online_reservation', 'event_ticketing']
    
    @property
    def booking_instructions(self):
        """Get appropriate booking instructions based on type"""
        if self.booking_type == 'walk_in':
            return "Walk-ins only - no reservations accepted"
        elif self.booking_type == 'call_reservation':
            return f"Call {self.phone} to make a reservation" if self.phone else "Call to make a reservation"
        elif self.booking_type == 'online_reservation':
            if self.external_booking_link:
                return "Reserve online through our system"
            return "Online reservations available"
        elif self.booking_type == 'event_ticketing':
            if self.external_booking_link:
                return "Get tickets through our ticketing partner"
            return "Tickets available online"
        return "Contact vendor for booking information"
    
    @property
    def booking_links_list(self):
        """Return a list of booking URLs from the text field"""
        if not self.external_booking_link:
            return []
        # Split by common separators and clean up
        links = []
        for line in self.external_booking_link.split('\n'):
            for url in line.split(','):
                url = url.strip()
                if url:
                    links.append(url)
        return links
    
    @property
    def average_rating(self):
        from django.db.models import Avg
        avg_rating = self.ratings.aggregate(Avg('rating'))['rating__avg']
        return round(avg_rating, 1) if avg_rating else 0
    
    @property
    def total_reviews(self):
        return self.ratings.count()
    
    @property
    def rating_distribution(self):
        from django.db.models import Count
        return self.ratings.values('rating').annotate(count=Count('rating')).order_by('rating')
    
    @property
    def service_badges(self):
        """Return list of service badges for display"""
        badges = []
        if self.accept_tour_partnership:
            badges.append({
                'text': 'Tour Partner',
                'class': 'bg-info',
                'icon': 'fas fa-hands-helping'
            })
        if self.catering_service:
            badges.append({
                'text': 'Catering Available',
                'class': 'bg-success',
                'icon': 'fas fa-utensils'
            })
        if self.halal:
            badges.append({
                'text': 'Halal Certified',
                'class': 'bg-success',
                'icon': 'fas fa-certificate'
            })
        if self.kosher:
            badges.append({
                'text': 'Kosher Certified',
                'class': 'bg-info text-dark',
                'icon': 'fas fa-star-of-david'
            })
        if self.vegetarian:
            badges.append({
                'text': 'Vegetarian',
                'class': 'bg-light text-dark',
                'icon': 'fas fa-leaf'
            })
        return badges
    
    class Meta:
        db_table = 'vendors'


class Event(models.Model):
    """Model for individual events hosted by ALL vendor types"""
    
    # ===== VENDOR RELATIONSHIP (ALL VENDOR TYPES) =====
    vendor = models.ForeignKey(
        Vendor, 
        on_delete=models.CASCADE, 
        related_name='events'
        # REMOVED: limit_choices_to - any vendor can create events
    )
    
    # ===== EVENT DETAILS (ALL VENDOR TYPES) =====
    event_name = models.CharField(
        max_length=200, 
        help_text="Name of this specific event"
    )
    event_description = models.TextField(blank=True)

    # Add these new fields:
    EVENT_TYPE_CHOICES = [
        ('seasonal_promotion', 'Seasonal Promotion'),
        ('food_fair', 'Food Fair'),
        ('popup_shop', 'Pop-up Food Shop'),
        ('workshop', 'Cooking Workshop'),
        # ('tasting', 'Tasting Event'),
        # ('collaboration', 'Chef Collaboration'),
        ('festival', 'Food Festival'),
        ('other', 'Other'),
    ]

    event_type = models.CharField(
        max_length=50,
        choices=EVENT_TYPE_CHOICES,
        default='other',
        help_text="Type of culinary event"
    )

    event_cuisine = models.ManyToManyField(
        'CuisineType',
        blank=True,
        related_name='events',
        help_text="Cuisine types featured in this event"
    )

    event_website = models.URLField(
        blank=True,
        max_length=200,
        help_text="Event website or registration page URL"
    )
    
    # ===== EVENT TIMING (ALL VENDOR TYPES) =====
    event_start_date = models.DateField(
        help_text="Start date for this event"
    )
    event_start_time = models.TimeField(
        null=True,
        blank=True,
        help_text="Start time for this event (optional)"
    )
    event_end_date = models.DateField(
        help_text="End date for this event"
    )
    event_end_time = models.TimeField(
        null=True,
        blank=True,
        help_text="End time for this event (optional)"
    )
    
    # ===== EVENT LOCATION (ALL VENDOR TYPES) =====
    event_address = models.TextField(
        help_text="Venue address for this specific event"
    )
    event_latitude = models.DecimalField(
        max_digits=10, 
        decimal_places=8, 
        null=True, 
        blank=True
    )
    event_longitude = models.DecimalField(
        max_digits=11, 
        decimal_places=8, 
        null=True, 
        blank=True
    )
    
    # ===== RECURRENCE INFO (ALL VENDOR TYPES) =====
    is_recurring = models.BooleanField(
        default=False, 
        help_text="Check if this specific event occurs regularly"
    )
    recurrence_pattern = models.CharField(
        max_length=100, 
        blank=True, 
        help_text="e.g., 'weekly', 'monthly_first_saturday'"
    )
    
    # ===== EVENT-SPECIFIC IMAGE (ALL VENDOR TYPES) =====
    event_pix = models.ImageField(upload_to='event_images/', null=True, blank=True)
    
    # ===== STATUS (ALL VENDOR TYPES) =====
    is_active = models.BooleanField(default=True)
    
    # ===== TIMESTAMPS (ALL VENDOR TYPES) =====
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.event_name} - {self.vendor.business_name}"
    
    @property
    def event_start_datetime(self):
        """Combine date and time for start"""
        if self.event_start_time:
            return timezone.make_aware(timezone.datetime.combine(self.event_start_date, self.event_start_time))
        return timezone.make_aware(timezone.datetime.combine(self.event_start_date, timezone.datetime.min.time()))
    
    @property
    def event_end_datetime(self):
        """Combine date and time for end"""
        if self.event_end_time:
            return timezone.make_aware(timezone.datetime.combine(self.event_end_date, self.event_end_time))
        return timezone.make_aware(timezone.datetime.combine(self.event_end_date, timezone.datetime.max.time()))
    
    @property
    def is_current(self):
        """Check if event is currently ongoing"""
        now = timezone.now()
        return bool(self.event_start_datetime <= now <= self.event_end_datetime)
    
    @property
    def is_upcoming(self):
        """Check if event is in the future"""
        now = timezone.now()
        return bool(self.event_start_datetime > now)
    
    @property
    def is_past(self):
        """Check if event has ended"""
        now = timezone.now()
        return bool(self.event_end_datetime < now)
    
    @property
    def display_time(self):
        """Display formatted time range"""
        if self.event_start_time and self.event_end_time:
            return f"{self.event_start_time.strftime('%I:%M %p')} - {self.event_end_time.strftime('%I:%M %p')}"
        elif self.event_start_time:
            return f"Starts at {self.event_start_time.strftime('%I:%M %p')}"
        elif self.event_end_time:
            return f"Until {self.event_end_time.strftime('%I:%M %p')}"
        else:
            return "All day"
    
    @property
    def display_date_range(self):
        """Display formatted date range"""
        if self.event_start_date == self.event_end_date:
            return self.event_start_date.strftime('%b %d, %Y')
        else:
            return f"{self.event_start_date.strftime('%b %d')} - {self.event_end_date.strftime('%b %d, %Y')}"
    
    class Meta:
        db_table = 'vendor_events'
        ordering = ['event_start_date', 'event_start_time']
        indexes = [
            models.Index(fields=['event_start_date', 'event_end_date']),
            models.Index(fields=['vendor', 'event_start_date']),
        ]


class CuisineType(models.Model):
    """Model for cuisine types to support multiple selections (ALL VENDOR TYPES)"""
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'cuisine_types'
        verbose_name = 'Cuisine Type'
        verbose_name_plural = 'Cuisine Types'


class MenuItem(models.Model):
    """Model for vendor menu items (ALL VENDOR TYPES)"""
    
    # ===== VENDOR RELATIONSHIP (ALL VENDOR TYPES) =====
    vendor = models.ForeignKey(
        Vendor, 
        on_delete=models.CASCADE, 
        related_name='menu_items'
    )
    dish_name = models.CharField(max_length=100)
    dish_price = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        help_text="Price in SGD", 
        null=True, 
        blank=True
    )
    dish_description = models.TextField(blank=True)
    dish_pix = models.ImageField(upload_to='menu_items/', null=True, blank=True)
    
    # ===== PRICE TYPE INDICATOR (ALL VENDOR TYPES) =====
    is_market_price = models.BooleanField(
        default=False,
        help_text="Check if this item has market/seasonal pricing"
    )
    
    # ===== DIETARY FLAGS (ALL VENDOR TYPES) =====
    # REMOVED: is_halal field - restaurant certification only, not self-declared
    is_vegetarian = models.BooleanField(default=False)
    is_vegan = models.BooleanField(default=False)
    
    # ===== TIMESTAMPS (ALL VENDOR TYPES) =====
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.dish_name} - {self.display_price}"
    
    @property
    def display_price(self):
        """Return formatted price or market price text"""
        if self.is_market_price:
            return "Market Price"
        elif self.dish_price:
            return f"${self.dish_price}"
        else:
            return "Price not set"
    
    @property
    def sort_price(self):
        """Return price for sorting (use 0 for market price items)"""
        return self.dish_price if self.dish_price and not self.is_market_price else 0
    
    class Meta:
        db_table = 'menu_items'
        verbose_name = 'Menu Item'
        verbose_name_plural = 'Menu Items'
        ordering = ['dish_name']