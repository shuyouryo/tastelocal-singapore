# users/views.py
from datetime import datetime
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.dateparse import parse_date
from django.views.decorators.http import require_POST
import json

from webapp.models import VendorRating
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .models import ItineraryNote

# Authentication Views

def register_view(request):
    """Handle user registration"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'redirect': '/'})
            return redirect('webapp:homepage')
        
        # Form is invalid
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'errors': form.errors})
    
    return render(request, 'users/register.html', {'form': CustomUserCreationForm()})

def user_login(request):
    """Handle user login - block admin users"""
    if request.user.is_authenticated:
        return redirect('webapp:homepage')
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        if form.is_valid():
            user = form.get_user()
            
            # Block admin users
            if user.is_staff or user.is_superuser:
                error_msg = "Admin users must use the Django admin login at /admin/"
                if is_ajax:
                    return JsonResponse({'success': False, 'error': error_msg, 'admin_redirect': True})
                messages.error(request, error_msg)
                return redirect('/admin/')
            
            login(request, user)
            
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'message': f'Welcome back, {user.username}!',
                    'redirect_url': reverse('webapp:homepage')
                })
            return redirect('webapp:homepage')
        
        # Invalid form
        error_msg = "Invalid email or password"
        if is_ajax:
            return JsonResponse({'success': False, 'error': error_msg})
        messages.error(request, error_msg)
        return redirect('webapp:homepage')
    
    # GET request
    return redirect('webapp:homepage')

def logout_view(request):
    """Handle user logout"""
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('webapp:homepage')

@login_required
def profile_view(request):
    """Display user profile"""
    if request.user.is_staff or request.user.is_superuser:
        return render(request, 'users/admin_profile.html', {'is_admin': True})
    return render(request, 'users/profile.html', {'is_admin': False})

@login_required
@require_POST
def update_profile(request):
    try:
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name  = request.POST.get('last_name', '')

        # if you really added these fields to your custom user
        if hasattr(user, 'nationality'):
            user.nationality = request.POST.get('nationality', '')
        if hasattr(user, 'phone_number'):
            user.phone_number = request.POST.get('phone_number', '')
        if hasattr(user, 'bio'):
            user.bio = request.POST.get('bio', '')
        
        # Handle date of birth
        dob_str = request.POST.get('date_of_birth', '')
        if dob_str and hasattr(user, 'date_of_birth'):
            user.date_of_birth = datetime.strptime(dob_str, '%Y-%m-%d').date()
        user.save()
            
        user.bio = request.POST.get('bio', '')
        user.save()
        
        # Format date for display
        dob_display = user.date_of_birth.strftime('%d/%m/%Y') if user.date_of_birth else None
        
        return JsonResponse({
            'success': True,
            'user': {
                'first_name': user.first_name,
                'last_name': user.last_name,
                'nationality_display': user.get_nationality_display(),
                'phone_number': user.phone_number,
                'date_of_birth_display': dob_display,
                'bio': user.bio
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# Password Reset

class AjaxPasswordResetView(PasswordResetView):
    """Your existing view - just improved"""
    
    def form_valid(self, form):
        # Check if email exists first
        email = form.cleaned_data.get('email')
        User = get_user_model()
        
        # Check if user exists and is active
        user_exists = User.objects.filter(email=email, is_active=True).exists()
        
        if not user_exists:
            # If it's an AJAX request, return JSON error
            if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': {
                        'email': ['No active account found with this email address.']
                    }
                })
            else:
                # For non-AJAX, use Django's default behavior
                return super().form_invalid(form)
        
        # If user exists, send the reset email
        response = super().form_valid(form)
        
        # If it's an AJAX request, return JSON success
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Password reset email sent successfully. Please check your inbox.'
            })
        return response
    
    def form_invalid(self, form):
        # Handle AJAX requests properly
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # Convert Django form errors to JSON
            errors_dict = {}
            for field, errors in form.errors.items():
                errors_dict[field] = [str(error) for error in errors]
            
            return JsonResponse({
                'success': False,
                'errors': errors_dict
            })
        return super().form_invalid(form)

# Itinerary Views

@login_required
def my_itinerary(request):
    """Display itinerary page"""
    return render(request, 'users/my_itinerary.html')

@login_required
def get_itinerary_notes(request):
    """Get itinerary notes for calendar"""
    date_str = request.GET.get('date')
    
    if date_str:
        date = parse_date(date_str)
        notes = ItineraryNote.objects.filter(user=request.user, date=date).order_by('order')
    else:
        notes = ItineraryNote.objects.filter(user=request.user).order_by('order')
    
    notes_data = [{
        'id': note.id,
        'date': note.date.isoformat(),
        'title': note.title,
        'content': note.content,
        'created_at': note.created_at.isoformat(),
        'order': note.order,
    } for note in notes]
    
    return JsonResponse({'notes': notes_data})

@login_required
@require_POST
def save_itinerary_note(request):
    """Save itinerary note"""
    try:
        date_str = request.POST.get('date')
        title = request.POST.get('title')
        content = request.POST.get('content')
        
        if not date_str or not title:
            return JsonResponse({'success': False, 'error': 'Date and title are required'})
        
        date = parse_date(date_str)
        note_id = request.POST.get('note_id')
        
        if note_id:
            note = get_object_or_404(ItineraryNote, id=note_id, user=request.user)
            note.title = title
            note.content = content
            note.save()
        else:
            # New note - set order
            order = ItineraryNote.objects.filter(user=request.user, date=date).count() + 1
            ItineraryNote.objects.create(
                user=request.user,
                date=date,
                title=title,
                content=content,
                order=order
            )
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_POST
def delete_itinerary_note(request):
    """Delete itinerary note"""
    try:
        data = json.loads(request.body)
        note_id = data.get('note_id')
        note = get_object_or_404(ItineraryNote, id=note_id, user=request.user)
        note.delete()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
@require_POST
def reorder_itinerary_notes(request):
    """Reorder itinerary notes"""
    try:
        data = json.loads(request.body)
        note_id = data.get('note_id')
        direction = data.get('direction')  # 'up' or 'down'
        
        note = get_object_or_404(ItineraryNote, id=note_id, user=request.user)
        notes = list(ItineraryNote.objects.filter(user=request.user, date=note.date).order_by('order'))
        
        current_index = next((i for i, n in enumerate(notes) if n.id == note.id), None)
        
        if current_index is None:
            return JsonResponse({'success': False, 'error': 'Note not found'})
        
        if direction == 'up' and current_index > 0:
            # Swap with previous
            prev_note = notes[current_index - 1]
            note.order, prev_note.order = prev_note.order, note.order
            note.save()
            prev_note.save()
            
        elif direction == 'down' and current_index < len(notes) - 1:
            # Swap with next
            next_note = notes[current_index + 1]
            note.order, next_note.order = next_note.order, note.order
            note.save()
            next_note.save()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

# Reviews View

@login_required
def my_reviews(request):
    """Display user's reviews"""
    reviews = VendorRating.objects.filter(user=request.user).select_related('vendor').order_by('vendor__business_name')
    return render(request, 'users/my_reviews.html', {'reviews': reviews})