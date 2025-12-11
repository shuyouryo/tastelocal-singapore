# tours/views.py
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import models
from vendors.models import Vendor, CuisineType
from .models import TourOperator, Tour, TourItinerary  # ADD TourItinerary here
from .forms import TourOperatorForm, TourForm

def tour_login(request):
    """Simple tour operator login"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Simple check - just verify user_type
            if getattr(user, 'user_type', None) == 'tour_operator':
                login(request, user)
                
                # Create tour operator profile if missing
                tour_operator, created = TourOperator.objects.get_or_create(
                    user=user,
                    defaults={
                        'company_name': f"{user.first_name} {user.last_name}",
                        'description': "Tour operator profile - please update your business details"
                    }
                )
                
                if created:
                    messages.info(request, "Welcome! Please complete your tour operator profile.")
                    return redirect('tours:dashboard')
                else:
                    messages.success(request, f"Welcome back, {tour_operator.company_name}!")
                    return redirect('tours:dashboard')
            else:
                messages.error(request, "This account does not have tour operator access.")
        else:
            messages.error(request, "Invalid username or password.")
    
    return render(request, 'tours/login.html')

def tour_logout(request):
    """Simple tour operator logout"""
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('tours:login')

# Tour Operator Required Decorator
def tour_operator_required(view_func):
    """Decorator that strictly requires tour operator user"""
    def wrapper(request, *args, **kwargs):
        # LOGIC: Centralized access control for all tour portal views
        if not request.user.is_authenticated:
            messages.error(request, "Please log in to access tour operator dashboard.")
            return redirect('tours:login')
        
        # LOGIC: Double validation - both user type and profile must exist
        if getattr(request.user, 'user_type', None) != 'tour_operator':
            messages.error(request, "Tour operator access required.")
            logout(request)
            return redirect('tours:login')
            
        try:
            TourOperator.objects.get(user=request.user)
            return view_func(request, *args, **kwargs)
        except TourOperator.DoesNotExist:
            # LOGIC: Auto-create profile if missing and redirect to dashboard
            TourOperator.objects.create(
                user=request.user,
                company_name=f"{request.user.first_name} {request.user.last_name}",
                description="Tour operator profile - please update your business details"
            )
            messages.info(request, "Welcome! Please complete your tour operator profile.")
            return redirect('tours:dashboard')
    return wrapper

@login_required
def tour_dashboard(request):
    tour_operator = get_object_or_404(TourOperator, user=request.user)
    tours_count = Tour.objects.filter(tour_operator=tour_operator).count()
    
    # Handle profile updates directly from dashboard
    if request.method == 'POST':
        form = TourOperatorForm(request.POST, instance=tour_operator)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('tours:dashboard')
    else:
        form = TourOperatorForm(instance=tour_operator)
    
    context = {
        'tour_operator': tour_operator,
        'tours_count': tours_count,
        'form': form,
    }
    return render(request, 'tours/dashboard.html', context)

@tour_operator_required
def tour_management(request):
    """Comprehensive tour management with itineraries"""
    tour_operator = get_object_or_404(TourOperator, user=request.user)
    tours = Tour.objects.filter(tour_operator=tour_operator).prefetch_related('itinerary').order_by('-created_at')
    vendors = Vendor.objects.filter(is_active=True, is_verified=True)
    
    context = {
        'tour_operator': tour_operator,
        'tours': tours,
        'vendors': vendors,
    }
    return render(request, 'tours/tour_management.html', context)

@tour_operator_required
def add_tour(request):
    """Add new tour"""
    tour_operator = get_object_or_404(TourOperator, user=request.user)
    
    if request.method == 'POST':
        form = TourForm(request.POST)
        if form.is_valid():
            tour = form.save(commit=False)
            tour.tour_operator = tour_operator
            tour.save()
            messages.success(request, "Tour added successfully!")
            return redirect('tours:tour_management')
    else:
        form = TourForm()
    
    context = {
        'tour_operator': tour_operator,
        'form': form,
    }
    return render(request, 'tours/tour_form.html', context)

@tour_operator_required
def edit_tour(request, tour_id):
    """Edit tour"""
    tour_operator = get_object_or_404(TourOperator, user=request.user)
    tour = get_object_or_404(Tour, id=tour_id, tour_operator=tour_operator)
    
    if request.method == 'POST':
        form = TourForm(request.POST, instance=tour)
        if form.is_valid():
            form.save()
            messages.success(request, "Tour updated successfully!")
            return redirect('tours:tour_management')
    else:
        form = TourForm(instance=tour)
    
    context = {
        'tour_operator': tour_operator,
        'form': form,
        'tour': tour,
    }
    return render(request, 'tours/tour_form.html', context)

@tour_operator_required
def delete_tour(request, tour_id):
    """Delete tour"""
    tour_operator = get_object_or_404(TourOperator, user=request.user)
    tour = get_object_or_404(Tour, id=tour_id, tour_operator=tour_operator)
    
    if request.method == 'POST':
        tour.delete()
        messages.success(request, "Tour deleted successfully!")
    
    return redirect('tours:tour_management')

@tour_operator_required
def add_itinerary(request, tour_id):
    """Add itinerary item to tour"""
    tour_operator = get_object_or_404(TourOperator, user=request.user)
    tour = get_object_or_404(Tour, id=tour_id, tour_operator=tour_operator)
    
    if request.method == 'POST':
        stop_order = request.POST.get('stop_order')
        vendor_id = request.POST.get('vendor')
        duration_minutes = request.POST.get('duration_minutes')
        description = request.POST.get('description')
        
        vendor = None
        if vendor_id:
            vendor = get_object_or_404(Vendor, id=vendor_id)
        
        # Handle nullable duration_minutes - allow 0 as valid value
        duration_value = None
        if duration_minutes and duration_minutes.strip():
            try:
                duration_value = int(duration_minutes)
                # If it's 0, we keep it as 0 (not None)
            except (ValueError, TypeError):
                duration_value = None
        
        TourItinerary.objects.create(
            tour=tour,
            stop_order=stop_order,
            vendor=vendor,
            duration_minutes=duration_value,
            description=description
        )
        
        messages.success(request, "Itinerary stop added successfully!")
    
    return redirect('tours:tour_management')

@tour_operator_required
def edit_itinerary(request, itinerary_id):
    """Edit itinerary item"""
    itinerary = get_object_or_404(TourItinerary, id=itinerary_id, tour__tour_operator__user=request.user)
    
    if request.method == 'POST':
        itinerary.stop_order = request.POST.get('stop_order')
        vendor_id = request.POST.get('vendor')
        duration_minutes = request.POST.get('duration_minutes')
        itinerary.description = request.POST.get('description')
        
        # Handle duration_minutes - allow 0 as valid value
        if duration_minutes and duration_minutes.strip():
            try:
                itinerary.duration_minutes = int(duration_minutes)
            except (ValueError, TypeError):
                itinerary.duration_minutes = None
        else:
            itinerary.duration_minutes = None
        
        if vendor_id:
            itinerary.vendor = get_object_or_404(Vendor, id=vendor_id)
        else:
            itinerary.vendor = None
        
        itinerary.save()
        messages.success(request, "Itinerary stop updated successfully!")
    
    return redirect('tours:tour_management')

@tour_operator_required
def delete_itinerary(request, itinerary_id):
    """Delete itinerary item"""
    itinerary = get_object_or_404(TourItinerary, id=itinerary_id, tour__tour_operator__user=request.user)
    
    if request.method == 'POST':
        itinerary.delete()
        messages.success(request, "Itinerary stop deleted successfully!")
    
    return redirect('tours:tour_management')

@tour_operator_required
def vendor_search(request):
    """Search for F&B vendor partners"""
    tour_operator = get_object_or_404(TourOperator, user=request.user)
    vendors = Vendor.objects.filter(is_active=True, is_verified=True)
    
    query = request.GET.get('q')
    if query:
        vendors = vendors.filter(
            models.Q(business_name__icontains=query) |
            models.Q(description__icontains=query) |
            models.Q(cuisine_types__name__icontains=query)
        ).distinct()
    
    context = {
        'tour_operator': tour_operator,
        'vendors': vendors,
        'query': query,
    }
    return render(request, 'tours/vendor_search.html', context)

@tour_operator_required
def vendor_list(request):
    """Vendor listing page for tour operators with simple filters"""
    vendors = Vendor.objects.filter(is_active=True).order_by('business_name')  # Alphabetical order
    
    # Get filter parameters
    query = request.GET.get('q', '')
    selected_vendor_types = request.GET.getlist('vendor_type')
    selected_cuisine_types = request.GET.getlist('cuisine_type')
    partnership_only = request.GET.get('partnership_only') == '1'
    halal_filter = request.GET.get('halal') == 'on'
    vegetarian_filter = request.GET.get('vegetarian') == 'on'
    catering_filter = request.GET.get('catering') == 'on'
    
    # Apply filters
    if query:
        vendors = vendors.filter(
            Q(business_name__icontains=query) |
            Q(description__icontains=query) |
            Q(cuisine_types__name__icontains=query)
        ).distinct()
    
    if selected_vendor_types:
        vendors = vendors.filter(vendor_type__in=selected_vendor_types)
    
    if selected_cuisine_types:
        vendors = vendors.filter(cuisine_types__id__in=selected_cuisine_types)
    
    if partnership_only:
        vendors = vendors.filter(accept_tour_partnership=True)
    
    if halal_filter:
        vendors = vendors.filter(halal=True)
    
    if vegetarian_filter:
        vendors = vendors.filter(vegetarian=True)
    
    if catering_filter:
        vendors = vendors.filter(catering_service=True)
    
    # Get available options for filters - only Restaurant and Food Stall
    VENDOR_TYPES = [
        ('restaurant', 'Restaurant'),
        ('stall', 'Food Stall'),
    ]
    
    cuisine_types = CuisineType.objects.all().order_by('name')
    
    context = {
        'vendors': vendors,
        'query': query,
        'selected_vendor_types': selected_vendor_types,
        'selected_cuisine_types': selected_cuisine_types,
        'partnership_only': partnership_only,
        'halal_filter': halal_filter,
        'vegetarian_filter': vegetarian_filter,
        'catering_filter': catering_filter,
        'vendor_types': VENDOR_TYPES,
        'cuisine_types': cuisine_types,
    }
    return render(request, 'tours/vendor_list.html', context)