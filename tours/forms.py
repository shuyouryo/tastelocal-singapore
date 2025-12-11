# tours/forms.py
from django import forms
from .models import TourOperator, Tour, TourItinerary

from django import forms
from .models import TourOperator, Tour, TourItinerary

class TourOperatorForm(forms.ModelForm):
    class Meta:
        model = TourOperator
        fields = [
            'company_name', 'description', 'business_phone', 'business_email', 'website',
            'booking_tourists_small', 'booking_tourists_medium', 'catering_tourists', 
            'kitchen_tour', 'chef_lessons'
        ]
        
        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 4, 
                'class': 'form-control',
                'placeholder': 'Describe your tour company and experiences...'
            }),
            'company_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your company name'
            }),
            'business_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+65 1234 5678'
            }),
            'business_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'contact@yourcompany.com'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://yourcompany.com'
            }),
            # Business Development Services checkboxes
            'booking_tourists_small': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'booking_tourists_medium': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'catering_tourists': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'kitchen_tour': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'chef_lessons': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class TourForm(forms.ModelForm):
    class Meta:
        model = Tour
        fields = [
            'name', 'tour_type', 'description', 
            'duration_minutes', 'max_participants', 'price',
            'is_active', 'is_featured'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'tour_type': forms.Select(attrs={'class': 'form-control'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_participants': forms.NumberInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class TourItineraryForm(forms.ModelForm):
    class Meta:
        model = TourItinerary
        fields = ['vendor', 'stop_order', 'duration_minutes', 'description']
        widgets = {
            'vendor': forms.Select(attrs={'class': 'form-control'}),
            'stop_order': forms.NumberInput(attrs={'class': 'form-control'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
        help_texts = {
            'stop_order': 'Order in which this stop appears in the tour (1, 2, 3, etc.)',
            'duration_minutes': 'Time spent at this vendor location',
        } 