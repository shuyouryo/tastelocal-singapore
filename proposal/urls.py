# proposal/urls.py
from django.urls import path
from . import views

app_name = 'proposal'

urlpatterns = [
    path('create/', views.create_proposal, name='create'),
    path('<int:pk>/', views.proposal_detail, name='detail'),
    path('<int:pk>/respond/', views.respond_proposal, name='respond'),
    path('mine/', views.my_proposals, name='my_proposals'),   # ← new
]