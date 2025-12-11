# users/admin.py - Enhanced Version
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from django import forms
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    """Custom form for creating users that automatically sets email = username"""
    class Meta:
        model = CustomUser
        fields = ('username', 'user_type', 'nationality', 'first_name', 'last_name', 'phone_number')
    
    def save(self, commit=True):
        # Set email equal to username before saving
        user = super().save(commit=False)
        user.email = user.username  # Auto-set email from username
        if commit:
            user.save()
        return user

class UserTypeFilter(admin.SimpleListFilter):
    title = _('User Type')
    parameter_name = 'user_type'

    def lookups(self, request, model_admin):
        return CustomUser.USER_TYPE_CHOICES

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(user_type=self.value())

class NationalityFilter(admin.SimpleListFilter):
    title = _('Nationality')
    parameter_name = 'nationality'

    def lookups(self, request, model_admin):
        # Show only nationalities that are actually used
        nationalities = CustomUser.objects.values_list('nationality', flat=True).distinct()
        choices = []
        for code, name in CustomUser.NATIONALITY_CHOICES:
            if code in nationalities:
                choices.append((code, name))
        return choices

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(nationality=self.value())

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # Use custom form for creating users
    add_form = CustomUserCreationForm
    
    # Display fields in list view
    list_display = (
        'email', 
        'username', 
        'get_user_type_display', 
        'get_nationality_display', 
        'first_name', 
        'last_name', 
        'phone_number', 
        'is_staff', 
        'is_active', 
        'date_joined'
    )
    
    list_filter = (
        UserTypeFilter,
        NationalityFilter,
        'is_staff', 
        'is_superuser', 
        'is_active', 
        'date_joined'
    )
    
    search_fields = (
        'username', 
        'first_name', 
        'last_name', 
        'email', 
        'phone_number',
        'user_type',
        'nationality'
    )
    
    list_editable = ('is_active', 'is_staff')
    
    ordering = ('-date_joined',)
    
    # Fieldsets for edit view - Email is now read-only since it matches username
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        (_('Personal Information'), {
            'fields': (
                'first_name', 
                'last_name', 
                'email',  # Now read-only, automatically set from username
            )
        }),
        (_('Profile Details'), {
            'fields': (
                'user_type',
                'nationality', 
                'phone_number', 
                'date_of_birth', 
                'bio'
            )
        }),
        (_('Permissions'), {
            'fields': (
                'is_active', 
                'is_staff', 
                'is_superuser', 
                'groups', 
                'user_permissions'
            ),
        }),
        (_('Important Dates'), {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )
    
    # Fieldsets for add view - Use proper password fields
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
        (_('Personal Information'), {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'user_type', 'nationality', 'phone_number'),
        }),
    )
    
    # Readonly fields - Added email since it's auto-generated
    readonly_fields = ('email', 'last_login', 'date_joined')
    
    # Custom methods for display
    def get_user_type_display(self, obj):
        return obj.get_user_type_display()
    get_user_type_display.short_description = 'User Type'
    get_user_type_display.admin_order_field = 'user_type'
    
    def get_nationality_display(self, obj):
        return obj.get_nationality_display()
    get_nationality_display.short_description = 'Nationality' 
    get_nationality_display.admin_order_field = 'nationality'
    
    # Override save method to ensure email always matches username
    def save_model(self, request, obj, form, change):
        if not change:  # For new users
            obj.email = obj.username
        else:  # For existing users - keep email in sync with username
            if obj.email != obj.username:
                obj.email = obj.username
        super().save_model(request, obj, form, change)
    
    # Actions
    actions = ['make_active', 'make_inactive', 'sync_emails']
    
    def make_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} users were successfully activated.')
    make_active.short_description = "Activate selected users"
    
    def make_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} users were successfully deactivated.')
    make_inactive.short_description = "Deactivate selected users"
    
    def sync_emails(self, request, queryset):
        """Action to sync emails with usernames for selected users"""
        updated_count = 0
        for user in queryset:
            if user.email != user.username:
                user.email = user.username
                user.save()
                updated_count += 1
        self.message_user(request, f'{updated_count} users had their emails synced with usernames.')
    sync_emails.short_description = "Sync emails with usernames"