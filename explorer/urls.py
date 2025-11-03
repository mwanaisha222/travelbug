
from django.urls import path
from django.urls import include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('destinations/', views.destination_list, name='destination_list'),
    path('activities/', views.activities_list, name='activities_list'),
    path('destinations/<int:destination_id>/activities/', views.activities_page, name='activities_page'),
    path('travelers/<int:traveler_id>/', views.traveler_profile, name='traveler_profile'),
    path('travelers/', views.travelers_list, name='travelers_list'),
    path('destinations/<int:destination_id>/reviews/', views.reviews_page, name='reviews_page'),
    path('reviews/', views.reviews_list, name='reviews_list'),
    path('destination/add/', views.destination_create, name='destination_create'),
    path('destinations/<int:destination_id>/reviews/add/', views.review_create, name='review_create'),
    path('travelers/edit/', views.traveler_edit, name='traveler_edit'),
    path('analytics/', views.analytics_dashboard, name='analytics'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/register/', views.register, name='register'),
]