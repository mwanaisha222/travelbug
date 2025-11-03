# explorer/forms.py
from django import forms
from .models import Destination
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Review, Traveler


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    name = forms.CharField(max_length=100, required=True)

    class Meta:
        model = User
        # 'name' is not a User field; keep username and email here. 'name' is handled separately
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']


class TravelerForm(forms.ModelForm):
    class Meta:
        model = Traveler
        fields = ['name', 'email', 'favorite_destination']

class DestinationForm(forms.ModelForm):
    class Meta:
        model = Destination
        fields = ['name', 'country', 'description', 'best_season', 'image']
        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': 'Describe what makes this destination unique and special...'
            }),
        }
        help_texts = {
            'name': 'Enter the official name of the destination',
            'country': 'Specify the country where this destination is located',
            'description': 'Provide a compelling description',
            'best_season': 'Indicate the ideal time of year to visit',
            'image': 'Upload a high-quality image (PNG, JPG, JPEG)',
        }