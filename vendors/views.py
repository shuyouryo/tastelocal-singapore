# vendors/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from .models import Vendor, MenuItem, Event
from .forms import VendorForm, MenuItemForm, EventForm
from tours.models import TourOperator

def vendor_login(request):
    """Simple vendor login"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Simple check - just verify user_type
            if getattr(user, 'user_type', None) == 'vendor':
                login(request, user)
                
                # Create vendor profile if missing
                vendor, created = Vendor.objects.get_or_create(
                    user=user,
                    defaults={
                        'business_name': f"{user.first_name} {user.last_name}",
                        'vendor_type': 'restaurant',
                        'description': "Vendor profile - please update your business details"
                    }
                )
                
                if created:
                    messages.info(request, "Welcome! Please complete your vendor profile.")
                    return redirect('vendors:profile')
                else:
                    messages.success(request, f"Welcome back, {vendor.business_name}!")
                    return redirect('vendors:dashboard')
            else:
                messages.error(request, "This account does not have vendor access.")
        else:
            messages.error(request, "Invalid username or password.")
    
    return render(request, 'vendors/login.html')

def vendor_logout_custom(request):
    """Simple vendor logout"""
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('vendors:login')

# Vendor Required Decorator
def vendor_required(view_func):
    """Decorator that strictly requires vendor user"""
    def wrapper(request, *args, **kwargs):
        # LOGIC: Centralized access control for all vendor portal views
        print(f"=== VENDOR REQUIRED DEBUG ===")
        print(f"Request path: {request.path}")
        print(f"User: {request.user}")
        print(f"Authenticated: {request.user.is_authenticated}")
        
        if not request.user.is_authenticated:
            messages.error(request, "Please log in to access vendor dashboard.")
            return redirect('vendors:login')
        
        # LOGIC: Double validation - both user type and profile must exist
        if getattr(request.user, 'user_type', None) != 'vendor':
            messages.error(request, "Vendor access required.")
            logout(request)
            return redirect('vendors:login')
            
        try:
            Vendor.objects.get(user=request.user)
            return view_func(request, *args, **kwargs)
        except Vendor.DoesNotExist:
            # LOGIC: Handle edge case where profile is missing
            messages.info(request, "Please complete your vendor profile.")
            return redirect('vendors:profile')
    return wrapper

@vendor_required
def vendor_dashboard(request):
    vendor = get_object_or_404(Vendor, user=request.user)
    menu_items_count = MenuItem.objects.filter(vendor=vendor).count()
    events_count = Event.objects.filter(vendor=vendor).count()
    upcoming_events = Event.objects.filter(vendor=vendor, event_start_date__gte=timezone.now())[:5]
    
    # Get booking links for dashboard display
    booking_links = vendor.booking_links_list
    
    context = {
        'vendor': vendor,
        'menu_items_count': menu_items_count,
        'events_count': events_count,
        'upcoming_events': upcoming_events,
        'booking_links': booking_links,
    }
    return render(request, 'vendors/dashboard.html', context)

@vendor_required
def vendor_profile(request):
    vendor = get_object_or_404(Vendor, user=request.user)
    
    if request.method == 'POST':
        form = VendorForm(request.POST, request.FILES, instance=vendor)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('vendors:profile')
    else:
        form = VendorForm(instance=vendor)
    
    # Get booking links for profile display
    booking_links = vendor.booking_links_list
    
    context = {
        'vendor': vendor,
        'form': form,
        'booking_links': booking_links,
    }
    return render(request, 'vendors/profile.html', context)

@vendor_required
def vendor_menu(request):
    vendor = get_object_or_404(Vendor, user=request.user)
    menu_items = MenuItem.objects.filter(vendor=vendor).order_by('dish_name')
    
    context = {
        'vendor': vendor,
        'menu_items': menu_items,
    }
    return render(request, 'vendors/menu.html', context)

@vendor_required
def add_menu_item(request):
    vendor = get_object_or_404(Vendor, user=request.user)
    
    if request.method == 'POST':
        form = MenuItemForm(request.POST, request.FILES)
        if form.is_valid():
            menu_item = form.save(commit=False)
            menu_item.vendor = vendor
            menu_item.save()
            messages.success(request, "Menu item added successfully!")
            return redirect('vendors:menu')
    else:
        form = MenuItemForm()
    
    context = {
        'vendor': vendor,
        'form': form,
    }
    return render(request, 'vendors/menu_form.html', context)

@vendor_required
def edit_menu_item(request, item_id):
    vendor = get_object_or_404(Vendor, user=request.user)
    menu_item = get_object_or_404(MenuItem, id=item_id, vendor=vendor)
    
    if request.method == 'POST':
        form = MenuItemForm(request.POST, request.FILES, instance=menu_item)
        if form.is_valid():
            form.save()
            messages.success(request, "Menu item updated successfully!")
            return redirect('vendors:menu')
    else:
        form = MenuItemForm(instance=menu_item)
    
    context = {
        'vendor': vendor,
        'form': form,
        'menu_item': menu_item,
    }
    return render(request, 'vendors/menu_form.html', context)

@vendor_required
def delete_menu_item(request, item_id):
    vendor = get_object_or_404(Vendor, user=request.user)
    menu_item = get_object_or_404(MenuItem, id=item_id, vendor=vendor)
    
    if request.method == 'POST':
        menu_item.delete()
        messages.success(request, "Menu item deleted successfully!")
    
    return redirect('vendors:menu')

@vendor_required
def vendor_events(request):
    vendor = get_object_or_404(Vendor, user=request.user)
    events = Event.objects.filter(vendor=vendor).order_by('-event_start_date')
    
    context = {
        'vendor': vendor,
        'events': events,
    }
    return render(request, 'vendors/events.html', context)

@vendor_required
def add_event(request):
    vendor = get_object_or_404(Vendor, user=request.user)
    
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.vendor = vendor
            event.save()
            messages.success(request, "Event added successfully!")
            return redirect('vendors:events')
    else:
        form = EventForm()
    
    context = {
        'vendor': vendor,
        'form': form,
    }
    return render(request, 'vendors/event_form.html', context)

@vendor_required
def edit_event(request, event_id):
    vendor = get_object_or_404(Vendor, user=request.user)
    event = get_object_or_404(Event, id=event_id, vendor=vendor)
    
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, "Event updated successfully!")
            return redirect('vendors:events')
    else:
        form = EventForm(instance=event)
    
    context = {
        'vendor': vendor,
        'form': form,
        'event': event,
    }
    return render(request, 'vendors/event_form.html', context)

@vendor_required
def delete_event(request, event_id):
    vendor = get_object_or_404(Vendor, user=request.user)
    event = get_object_or_404(Event, id=event_id, vendor=vendor)
    
    if request.method == 'POST':
        event.delete()
        messages.success(request, "Event deleted successfully!")
    
    return redirect('vendors:events')

@vendor_required
def vendor_booking_settings(request):
    """View for managing booking settings and URLs"""
    vendor = get_object_or_404(Vendor, user=request.user)
    
    if request.method == 'POST':
        form = VendorForm(request.POST, instance=vendor)
        if form.is_valid():
            form.save()
            messages.success(request, "Booking settings updated successfully!")
            return redirect('vendors:booking_settings')
    else:
        form = VendorForm(instance=vendor)
    
    # Get parsed booking links for display
    booking_links = vendor.booking_links_list
    
    context = {
        'vendor': vendor,
        'form': form,
        'booking_links': booking_links,
    }
    return render(request, 'vendors/booking_settings.html', context)

def tour_operators_list(request):
    if not hasattr(request.user, 'vendor'):
        return redirect('vendors:login')
    
    tour_operators = TourOperator.objects.filter(is_verified=True)
    
    context = {
        'vendor': request.user.vendor,
        'tour_operators': tour_operators,
        'verified_count': tour_operators.count(),
        'insured_count': tour_operators.filter(has_insurance=True).count(),
        'natas_count': tour_operators.filter(natas_member=True).count(),
    }
    
    return render(request, 'vendors/tour_operators.html', context)

