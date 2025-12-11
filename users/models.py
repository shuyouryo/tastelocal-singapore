# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # User type choices
    USER_TYPE_CHOICES = [
        ('local', 'Local Singaporean Resident'),
        ('tourist', 'Tourist'),
        ('vendor', 'F&B Vendor'),
        ('tour_operator', 'Tour Operator'),
    ]
    
    # Nationality choices - you can expand this list
    NATIONALITY_CHOICES = [
        ('singaporean', 'Singaporean'),
        ('malaysian', 'Malaysian'),
        ('indonesian', 'Indonesian'),
        ('chinese', 'Chinese'),
        ('indian', 'Indian'),
        ('filipino', 'Filipino'),
        ('thai', 'Thai'),
        ('vietnamese', 'Vietnamese'),
        ('british', 'British'),
        ('american', 'American'),
        ('australian', 'Australian'),
        ('canadian', 'Canadian'),
        ('japanese', 'Japanese'),
        ('korean', 'Korean'),
        ('german', 'German'),
        ('french', 'French'),
        ('other', 'Other'),
    ]
    
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='tourist',
        verbose_name='User Type'
    )
    nationality = models.CharField(
        max_length=50,
        choices=NATIONALITY_CHOICES,
        default='singaporean',
        verbose_name='Nationality'
    )
    phone_number = models.CharField(max_length=15, blank=True)
    
    # Additional fields that might be useful
    date_of_birth = models.DateField(null=True, blank=True, verbose_name='Date of Birth')
    bio = models.TextField(blank=True, verbose_name='About Me')
    
    # Add related_name to avoid clashes
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='customuser_set',
        related_query_name='user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='customuser_set',
        related_query_name='user',
    )
    
    def __str__(self):
        return self.email
    
    def can_rate_vendors(self):
        """Check if user can rate vendors (only locals and tourists)"""
        return self.user_type in ['local', 'tourist']
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

class ItineraryNote(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='itinerary_notes')
    date = models.DateField()
    title = models.CharField(max_length=200)
    content = models.TextField()
    order = models.PositiveIntegerField(default=0)  # This field is crucial for reordering
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'date', 'title']
        ordering = ['date', 'order', '-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.title}"