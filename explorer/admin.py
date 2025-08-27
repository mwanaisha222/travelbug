from django.contrib import admin
from .models import Destination, Activity, Traveler, Review

admin.site.register(Destination)
admin.site.register(Activity)
admin.site.register(Traveler)
admin.site.register(Review)