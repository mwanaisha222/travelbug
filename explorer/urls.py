
from django.urls import path
from . import views

urlpatterns = [
    path('', views.destination_list, name='destination_list'),  # Changed from 'destinations/' to ''
    path('destinations/<int:destination_id>/activities/', views.activities_page, name='activities_page'),
    path('travelers/<int:traveler_id>/', views.traveler_profile, name='traveler_profile'),
    path('destinations/<int:destination_id>/reviews/', views.reviews_page, name='reviews_page'),
    path('destination/add/', views.destination_create, name='destination_create'),
]