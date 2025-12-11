# tastelocal/utils/domain_helpers.py
def is_webapp_user(request):
    """Check if current session is a webapp user session"""
    return (request.user.is_authenticated and 
            request.user.user_type in ['local', 'tourist', 'vendor', 'tour_operator'] and
            getattr(request, 'session_domain', 'webapp') == 'webapp')

def is_vendor_dashboard_session(request):
    """Check if current session is a vendor dashboard session"""
    return (request.user.is_authenticated and 
            request.user.user_type == 'vendor' and
            getattr(request, 'session_domain', None) == 'vendor_dashboard')

def is_tour_dashboard_session(request):
    """Check if current session is a tour dashboard session"""
    return (request.user.is_authenticated and 
            request.user.user_type == 'tour_operator' and
            getattr(request, 'session_domain', None) == 'tour_dashboard')

def is_admin_session(request):
    """Check if current session is an admin session"""
    return (request.user.is_authenticated and 
            request.user.is_staff and
            getattr(request, 'session_domain', None) == 'admin')