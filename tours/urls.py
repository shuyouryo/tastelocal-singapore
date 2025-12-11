# tours/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'tours'

urlpatterns = [
    # Authentication
    path('', views.tour_login, name='login'),
    path('login/', views.tour_login, name='login'),
    path('logout/', views.tour_logout, name='logout'),
    
    # Dashboard (now includes profile editing)
    path('dashboard/', views.tour_dashboard, name='dashboard'),
    
    # Tours Management
    path('tours/', views.tour_management, name='tour_management'),  # Updated to use management view
    path('tours/add/', views.add_tour, name='add_tour'),
    path('tours/<int:tour_id>/edit/', views.edit_tour, name='edit_tour'),
    path('tours/<int:tour_id>/delete/', views.delete_tour, name='delete_tour'),
    path('tours/<int:tour_id>/itinerary/add/', views.add_itinerary, name='add_itinerary'),
    path('itinerary/<int:itinerary_id>/edit/', views.edit_itinerary, name='edit_itinerary'),
    path('itinerary/<int:itinerary_id>/delete/', views.delete_itinerary, name='delete_itinerary'),
    
    # Vendor Search
    path('vendors/', views.vendor_list, name='vendor_list'),
    path('vendors/', views.vendor_search, name='vendor_search'),
]