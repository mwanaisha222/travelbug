from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login
from django.contrib import messages
from .forms import RegistrationForm, ReviewForm, TravelerForm
from .models import Destination, Activity, Traveler, Review
from .forms import DestinationForm
from . import analytics



def destination_list(request):
    destinations = Destination.objects.all()
    return render(request, 'explorer/destination_list.html', {'destinations': destinations})


def home(request):
    """Home page — show a hero and a few featured destinations."""
    featured = Destination.objects.all()[:6]
    return render(request, 'explorer/home.html', {'featured': featured})

def destination_create(request):
    # Only allow staff (admin) users to create destinations
    if not request.user.is_authenticated or not request.user.is_staff:
        messages.warning(request, 'Only administrators can add new destinations.')
        return redirect('login')
    
    if request.method == 'POST':
        form = DestinationForm(request.POST, request.FILES)
        if form.is_valid():
            destination = form.save()
            messages.success(request, f'Destination "{destination.name}" has been successfully created!')
            return redirect('destination_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = DestinationForm()
    
    # Get statistics for the admin dashboard
    context = {
        'form': form,
        'total_destinations': Destination.objects.count(),
        'total_reviews': Review.objects.count(),
        'total_travelers': Traveler.objects.count(),
    }
    return render(request, 'explorer/destination_form.html', context)

def register(request):
    """Registration view that collects username, name and email and creates
    both a Django User and a Traveler profile linked to it."""
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create a Traveler profile linked to this User
            Traveler.objects.create(name=form.cleaned_data.get('name'),
                                    email=form.cleaned_data.get('email') or '',
                                    user=user)
            login(request, user)
            return redirect('destination_list')
    else:
        form = RegistrationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def review_create(request, destination_id):
    destination = get_object_or_404(Destination, pk=destination_id)
    # get or create the Traveler profile for the logged-in user
    traveler, _ = Traveler.objects.get_or_create(user=request.user, defaults={'name': request.user.username, 'email': request.user.email or ''})
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.destination = destination
            review.traveler = traveler
            review.save()
            return redirect('reviews_page', destination_id=destination.id)
    else:
        form = ReviewForm()
    return render(request, 'explorer/review_form.html', {'form': form, 'destination': destination})


@login_required
def traveler_edit(request):
    # Allow a logged in user to edit their Traveler profile
    traveler, _ = Traveler.objects.get_or_create(user=request.user, defaults={'name': request.user.username, 'email': request.user.email or ''})
    if request.method == 'POST':
        form = TravelerForm(request.POST, instance=traveler)
        if form.is_valid():
            form.save()
            return redirect('travelers_list')
    else:
        form = TravelerForm(instance=traveler)
    return render(request, 'explorer/traveler_form.html', {'form': form})

def activities_page(request, destination_id):
    destination = get_object_or_404(Destination, pk=destination_id)
    activities = destination.activities.all()
    return render(request, 'explorer/activities.html', {'destination': destination, 'activities': activities})

def activities_list(request):
    # Show all activities across destinations
    activities = Activity.objects.select_related('destination').all()
    return render(request, 'explorer/activities_list.html', {'activities': activities})

def traveler_profile(request, traveler_id):
    traveler = get_object_or_404(Traveler, pk=traveler_id)
    # Get all reviews by this traveler
    reviews = Review.objects.filter(traveler=traveler).select_related('destination')
    return render(request, 'explorer/traveler_profile.html', {'traveler': traveler, 'reviews': reviews})

def travelers_list(request):
    travelers = Traveler.objects.select_related('favorite_destination').all()
    return render(request, 'explorer/travelers_list.html', {'travelers': travelers})

def reviews_page(request, destination_id):
    destination = get_object_or_404(Destination, pk=destination_id)
    reviews = destination.reviews.all()
    return render(request, 'explorer/reviews.html', {'destination': destination, 'reviews': reviews})

def reviews_list(request):
    # Show recent reviews across destinations
    reviews = Review.objects.select_related('traveler', 'destination').all()
    return render(request, 'explorer/reviews_list.html', {'reviews': reviews})

def analytics_dashboard(request):
    """Analytics dashboard with data visualizations"""
    context = {
        'summary': analytics.get_analytics_summary(),
        'destination_popularity': analytics.generate_destination_popularity_bar(),
        'destination_ratings': analytics.generate_destination_ratings_bar(),
        'activity_distribution': analytics.generate_activity_distribution_pie(),
        'traveler_preferences': analytics.generate_traveler_preferences_pie(),
        'rating_trends': analytics.generate_rating_trends_line(),
        'seasonal_heatmap': analytics.generate_seasonal_heatmap(),
        'rating_distribution': analytics.generate_rating_distribution(),
        'top_destinations_comparison': analytics.generate_top_destinations_comparison(),
    }
    return render(request, 'explorer/analytics.html', context)
