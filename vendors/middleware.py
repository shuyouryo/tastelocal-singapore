# # vendors/middleware.py
# from django.shortcuts import redirect
# from django.urls import reverse
# from django.contrib import messages
# from django.contrib.auth import logout
# from .models import Vendor

# class VendorAccessMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         # Only apply to vendor URLs (exclude login and static files)
#         if (request.path.startswith('/vendors/') and 
#             not request.path.startswith('/vendors/login/') and
#             not request.path.startswith('/vendors/static/') and
#             request.path != '/vendors/login/'):
            
#             if not request.user.is_authenticated:
#                 return redirect('vendors:login')
            
#             # Strict vendor check for all vendor paths
#             try:
#                 Vendor.objects.get(user=request.user)
#             except Vendor.DoesNotExist:
#                 # User is authenticated but not a vendor - clear session and redirect
#                 logout(request)
#                 messages.error(request, "Vendor access required. Please log in with a vendor account.")
#                 return redirect('vendors:login')
        
#         response = self.get_response(request)
#         return response