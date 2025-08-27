from django.shortcuts import render,redirect, get_object_or_404
from .models import Destination, Activity, Traveler, Review
from .forms import DestinationForm



def destination_list(request):
    destinations = Destination.objects.all()
    return render(request, 'explorer/destination_list.html', {'destinations': destinations})

def destination_create(request):
    if request.method == 'POST':
        form = DestinationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('destination_list')
    else:
        form = DestinationForm()
    return render(request, 'explorer/destination_form.html', {'form': form})

def activities_page(request, destination_id):
    destination = get_object_or_404(Destination, pk=destination_id)
    activities = destination.activities.all()
    return render(request, 'explorer/activities.html', {'destination': destination, 'activities': activities})

def traveler_profile(request, traveler_id):
    traveler = get_object_or_404(Traveler, pk=traveler_id)
    return render(request, 'explorer/traveler_profile.html', {'traveler': traveler})

def reviews_page(request, destination_id):
    destination = get_object_or_404(Destination, pk=destination_id)
    reviews = destination.reviews.all()
    return render(request, 'explorer/reviews.html', {'destination': destination, 'reviews': reviews})