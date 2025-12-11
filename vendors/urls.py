# vendors/urls.py
from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = 'vendors'

urlpatterns = [
    # Root redirect to login
    path('', RedirectView.as_view(pattern_name='vendors:login', permanent=False)),
    
    # Authentication
    path('login/', views.vendor_login, name='login'),
    path('logout/', views.vendor_logout_custom, name='logout'),
    
    # All other paths are protected
    path('dashboard/', views.vendor_dashboard, name='dashboard'),
    path('profile/', views.vendor_profile, name='profile'),
    path('menu/', views.vendor_menu, name='menu'),
    path('menu/add/', views.add_menu_item, name='add_menu_item'),
    path('menu/<int:item_id>/edit/', views.edit_menu_item, name='edit_menu_item'),
    path('menu/<int:item_id>/delete/', views.delete_menu_item, name='delete_menu_item'),
    path('events/', views.vendor_events, name='events'),
    path('events/add/', views.add_event, name='add_event'),
    path('events/<int:event_id>/edit/', views.edit_event, name='edit_event'),
    path('events/<int:event_id>/delete/', views.delete_event, name='delete_event'),
    path('booking-settings/', views.vendor_booking_settings, name='booking_settings'),

    # Business Partnerships
    path('tour-operators/', views.tour_operators_list, name='tour_operators'),
]