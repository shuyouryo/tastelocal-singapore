# webapp/urls.py
"""
URL routes for main website app - public facing content
"""

from django.urls import path
from . import views

app_name = 'webapp'

urlpatterns = [
    # Public pages
    path('', views.homepage, name='homepage'),
    path('places-eat/', views.places_eat, name='places_eat'),
    path('search/', views.search, name='search'),

    # Foodie Articles pages
    path('foodie-stories/', views.foodie_stories, name='foodie_stories'),
    path('articles/<slug:slug>/', views.article_detail, name='article_detail'),

    # Tours pages
    path('tours-experiences/', views.tours_experiences, name='tours_experiences'),
    path('tours-experiences/tour/<int:tour_id>/', views.tour_detail, name='tour_detail'),
    
    # Vendor category pages
    path('places-eat/restaurants/', views.restaurants, name='restaurants'),
    path('places-eat/food-stalls/', views.food_stalls, name='food_stalls'),
    path('places-eat/culinary-events/', views.culinary_events, name='culinary_events'),

    # Vendor details pages
    path('places-eat/restaurants/<int:vendor_id>/', views.restaurant_detail, name='restaurant_detail'),
    path('places-eat/food-stall/<int:vendor_id>/', views.food_stall_detail, name='food_stall_detail'),
    path('places-eat/culinary-event/<int:event_id>/', views.culinary_event_detail, name='culinary_event_detail'),

    # Vendor review pages
    path('vendor/<int:vendor_id>/rate/', views.submit_rating, name='submit_rating'),
    
    # Tours & Experiences
    path('tours-experiences/', views.tours_experiences, name='tours_experiences'),
    path('tours-experiences/guided-tours/', views.guided_tours, name='guided_tours'),
    path('tours-experiences/tour/<int:tour_id>/', views.tour_detail, name='tour_detail'),
    path('tours-experiences/foodie-crawls/', views.foodie_crawls, name='foodie_crawls'),

    # Company pages
    path('about-us/', views.about_us, name='about_us'),
    path('our-mission/', views.our_mission, name='our_mission'),
    path('business-partners/', views.business_partners, name='business_partners'),
    path('contact/', views.contact, name='contact'),

    # Legal pages
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-service/', views.terms_service, name='terms_service'),
    path('contact/', views.contact, name='contact'),

]