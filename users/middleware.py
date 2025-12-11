# users/middleware.py (create this file)
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages

class AdminWebappAccessControlMiddleware:
    """Prevent admin users from accessing webapp features"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        # URLs that admin users should NOT access
        self.restricted_paths = [
            '/users/profile/',
            '/users/my_itinerary/',
            '/users/my_reviews/',
            # Add other webapp paths admin shouldn't use
        ]
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Check if user is staff/superuser trying to access webapp features
        if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
            for path in self.restricted_paths:
                if request.path.startswith(path):
                    messages.warning(
                        request, 
                        "Admin users should use the Django admin interface."
                    )
                    return redirect('/admin/')
        
        return response