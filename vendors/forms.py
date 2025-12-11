# vendors/forms.py - UPDATED VERSION
from django import forms
from .models import Vendor, MenuItem, Event

class VendorForm(forms.ModelForm):
    class Meta:
        model = Vendor
        # Let Django automatically determine fields from the model
        fields = '__all__'
        exclude = ['user', 'is_verified', 'is_featured', 'is_active', 'created_at', 'updated_at']
        
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500'}),
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500'}),
            'opening_hours': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500'}),
            'reservation_instructions': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500'}),
            'external_booking_link': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500', 'placeholder': 'Enter one URL per line or separate with commas'}),
            'business_name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500'}),
            'phone': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500'}),
            'website': forms.URLInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500'}),
            'max_group_size': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500'}),
            'advance_notice_hours': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500'}),
            'vendor_type': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500'}),
            'booking_type': forms.Select(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500'}),
            'latitude': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500', 'step': '0.00000001'}),
            'longitude': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500', 'step': '0.00000001'}),
            # ADDED: Checkbox widgets for dietary certifications
            'halal': forms.CheckboxInput(attrs={'class': 'rounded border-gray-300 text-orange-500 focus:ring-orange-500'}),
            'kosher': forms.CheckboxInput(attrs={'class': 'rounded border-gray-300 text-orange-500 focus:ring-orange-500'}),
            'vegetarian': forms.CheckboxInput(attrs={'class': 'rounded border-gray-300 text-orange-500 focus:ring-orange-500'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Update help texts for reservation-related fields
        self.fields['booking_type'].help_text = "How customers can make reservations"
        self.fields['external_booking_link'].help_text = "URL(s) for reservations. Multiple URLs can be separated by commas or new lines."
        self.fields['advance_notice_hours'].help_text = "Required advance notice for reservations in hours"
        self.fields['max_group_size'].help_text = "Maximum group size allowed for reservations (0 = no limit)"
        self.fields['reservation_instructions'].help_text = "Specific instructions for making reservations"

class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = '__all__'
        exclude = ['vendor', 'created_at', 'updated_at']
        
        widgets = {
            'dish_description': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500'}),
            'dish_name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500'}),
            'dish_price': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500', 'step': '0.01'}),
            'is_market_price': forms.CheckboxInput(attrs={'class': 'rounded border-gray-300 text-orange-500 focus:ring-orange-500'}),
            'is_vegetarian': forms.CheckboxInput(attrs={'class': 'rounded border-gray-300 text-orange-500 focus:ring-orange-500'}),
            'is_vegan': forms.CheckboxInput(attrs={'class': 'rounded border-gray-300 text-orange-500 focus:ring-orange-500'}),
        }

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = '__all__'
        exclude = ['vendor', 'created_at', 'updated_at']
        
        widgets = {
            'event_description': forms.Textarea(attrs={'rows': 4, 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500'}),
            'event_address': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500'}),
            # UPDATED: Separate date and time widgets
            'event_start_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500'}),
            'event_start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500'}),
            'event_end_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500'}),
            'event_end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500'}),
            # ADDED: Event website widget
            'event_website': forms.URLInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500', 'placeholder': 'https://example.com'}),
            'event_name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500'}),
            'recurrence_pattern': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500'}),
            'event_latitude': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500', 'step': '0.00000001'}),
            'event_longitude': forms.NumberInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-orange-500', 'step': '0.00000001'}),
            'is_recurring': forms.CheckboxInput(attrs={'class': 'rounded border-gray-300 text-orange-500 focus:ring-orange-500'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'rounded border-gray-300 text-orange-500 focus:ring-orange-500'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        event_start_date = cleaned_data.get('event_start_date')
        event_end_date = cleaned_data.get('event_end_date')
        
        # Validate that end date is not before start date
        if event_start_date and event_end_date and event_end_date < event_start_date:
            raise forms.ValidationError({
                'event_end_date': 'Event end date must be on or after the start date.'
            })
        
        return cleaned_data