# tastelocal/middleware/session_domains.py
from django.conf import settings

class SessionDomainMiddleware:
    """
    Enhanced session middleware for better portal separation
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Identify which portal/section this request is for
        current_path = request.path
        
        if current_path.startswith('/admin/'):
            section = 'admin'
        elif current_path.startswith('/vendors/'):
            section = 'vendor'  
        elif current_path.startswith('/tours/'):  # CORRECTED
            section = 'tours'  # CORRECTED
        else:
            section = 'webapp'
        
        # Store in request for other middleware to use
        request.portal_section = section
        
        response = self.get_response(request)
        
        # Optional: Add section identifier to response headers for debugging
        if hasattr(response, 'headers'):
            response.headers['X-Portal-Section'] = section
            
        return response