# users/urls.py
from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),

    # Password reset function
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='users/password_reset.html',
             email_template_name='users/password_reset_email.html',
             subject_template_name='users/password_reset_subject.txt',
             success_url='/users/password-reset/done/'  # Make sure this matches
         ), 
         name='password_reset'),
    
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='users/password_reset_done.html'
         ), 
         name='password_reset_done'),
    
    # IMPORTANT: This pattern name must be 'password_reset_confirm'
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='users/password_reset_confirm.html',
             success_url='/users/password-reset-complete/'
         ), 
         name='password_reset_confirm'),  # This name is crucial!
    
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='users/password_reset_complete.html'
         ), 
         name='password_reset_complete'),

    # My Itinerary & API endpoints
    path('my-itinerary/', views.my_itinerary, name='my_itinerary'),
    path('itinerary/notes/', views.get_itinerary_notes, name='get_itinerary_notes'),
    path('itinerary/save-note/', views.save_itinerary_note, name='save_itinerary_note'),
    path('itinerary/delete-note/', views.delete_itinerary_note, name='delete_itinerary_note'), 
    path('itinerary/reorder-notes/', views.reorder_itinerary_notes, name='reorder_itinerary_notes'),

    # My Reviews & API endpoints
    path('my-reviews/', views.my_reviews, name='my_reviews'),
]