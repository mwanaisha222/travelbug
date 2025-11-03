"""
Unit tests for Explorer views.
Tests all view functions including GET/POST requests, authentication, and edge cases.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import Http404
from decimal import Decimal
from explorer.models import Destination, Activity, Traveler, Review
from explorer.forms import DestinationForm


class DestinationListViewTest(TestCase):
    """Test cases for the destination_list view."""
    
    def setUp(self):
        """Set up test data and client."""
        self.client = Client()
        self.url = reverse('destination_list')
        
        # Create test destinations
        self.destination1 = Destination.objects.create(
            name='Paris',
            country='France',
            description='The City of Light',
            best_season='Spring'
        )
        self.destination2 = Destination.objects.create(
            name='Tokyo',
            country='Japan',
            description='Modern metropolis',
            best_season='Autumn'
        )
    
    def test_destination_list_view_get(self):
        """Test GET request to destination list view."""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Paris')
        self.assertContains(response, 'Tokyo')
        self.assertContains(response, 'TravelBucket')
        self.assertTemplateUsed(response, 'explorer/destination_list.html')
    
    def test_destination_list_context(self):
        """Test context data passed to template."""
        response = self.client.get(self.url)
        
        self.assertIn('destinations', response.context)
        destinations = response.context['destinations']
        self.assertEqual(destinations.count(), 2)
        self.assertIn(self.destination1, destinations)
        self.assertIn(self.destination2, destinations)
    
    def test_destination_list_empty(self):
        """Test destination list view with no destinations."""
        Destination.objects.all().delete()
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No destinations available')
        self.assertEqual(response.context['destinations'].count(), 0)
    
    def test_destination_list_with_images(self):
        """Test destination list displays images correctly."""
        # Create a test image file
        test_image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'fake image content',
            content_type='image/jpeg'
        )
        
        destination_with_image = Destination.objects.create(
            name='Rome',
            country='Italy',
            description='Historic city',
            best_season='Spring',
            image=test_image
        )
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Rome')


class DestinationCreateViewTest(TestCase):
    """Test cases for the destination_create view."""
    
    def setUp(self):
        """Set up test data and client."""
        self.client = Client()
        self.url = reverse('destination_create')
        self.valid_data = {
            'name': 'Barcelona',
            'country': 'Spain',
            'description': 'Beautiful Mediterranean city',
            'best_season': 'Spring'
        }
        # Create a staff user for admin-restricted tests
        from django.contrib.auth.models import User
        self.staff_user = User.objects.create_user(
            username='admin',
            password='adminpass',
            is_staff=True
        )
        self.client.login(username='admin', password='adminpass')
    
    def test_destination_create_view_get(self):
        """Test GET request to destination create view."""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'explorer/destination_form.html')
        self.assertIsInstance(response.context['form'], DestinationForm)
    
    def test_destination_create_post_valid(self):
        """Test POST request with valid data."""
        response = self.client.post(self.url, self.valid_data)
        
        # Should redirect to destination list after successful creation
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('destination_list'))
        
        # Check destination was created
        self.assertTrue(Destination.objects.filter(name='Barcelona').exists())
        destination = Destination.objects.get(name='Barcelona')
        self.assertEqual(destination.country, 'Spain')
        self.assertEqual(destination.description, 'Beautiful Mediterranean city')
    
    def test_destination_create_post_invalid(self):
        """Test POST request with invalid data."""
        invalid_data = self.valid_data.copy()
        invalid_data['name'] = ''  # Empty name should be invalid
        
        response = self.client.post(self.url, invalid_data)
        
        # Should not redirect, should show form with errors
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'explorer/destination_form.html')
        self.assertContains(response, 'This field is required')
        
        # Check destination was not created
        self.assertFalse(Destination.objects.filter(country='Spain').exists())
    
    def test_destination_create_with_image(self):
        """Test creating destination with image upload."""
        # Create a simple 1x1 pixel PNG image
        from PIL import Image
        import io
        
        image = Image.new('RGB', (1, 1), color='red')
        image_io = io.BytesIO()
        image.save(image_io, format='PNG')
        image_io.seek(0)
        
        test_image = SimpleUploadedFile(
            name='test_image.png',
            content=image_io.read(),
            content_type='image/png'
        )
        
        data_with_image = self.valid_data.copy()
        data_with_image['image'] = test_image
        
        response = self.client.post(self.url, data_with_image)
        
        self.assertEqual(response.status_code, 302)
        destination = Destination.objects.get(name='Barcelona')
        self.assertTrue(destination.image)
    
    def test_destination_create_duplicate_name(self):
        """Test creating destination with duplicate name (should be allowed)."""
        # Create first destination
        Destination.objects.create(**self.valid_data)
        
        # Try to create another with same name
        response = self.client.post(self.url, self.valid_data)
        
        self.assertEqual(response.status_code, 302)
        # Should be allowed - both destinations created
        self.assertEqual(Destination.objects.filter(name='Barcelona').count(), 2)


class ActivitiesPageViewTest(TestCase):
    """Test cases for the activities_page view."""
    
    def setUp(self):
        """Set up test data and client."""
        self.client = Client()
        
        self.destination = Destination.objects.create(
            name='London',
            country='UK',
            description='Historic capital city',
            best_season='Summer'
        )
        
        self.activity1 = Activity.objects.create(
            name='Tower of London',
            destination=self.destination,
            description='Historic castle',
            cost_estimate=Decimal('28.50')
        )
        self.activity2 = Activity.objects.create(
            name='British Museum',
            destination=self.destination,
            description='World-class museum',
            cost_estimate=Decimal('0.00')  # Free entry
        )
        
        self.url = reverse('activities_page', kwargs={'destination_id': self.destination.id})
    
    def test_activities_page_view_get(self):
        """Test GET request to activities page."""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'London')
        self.assertContains(response, 'Tower of London')
        self.assertContains(response, 'British Museum')
        self.assertTemplateUsed(response, 'explorer/activities.html')
    
    def test_activities_page_context(self):
        """Test context data passed to template."""
        response = self.client.get(self.url)
        
        self.assertIn('destination', response.context)
        self.assertIn('activities', response.context)
        
        self.assertEqual(response.context['destination'], self.destination)
        activities = response.context['activities']
        self.assertEqual(activities.count(), 2)
        self.assertIn(self.activity1, activities)
        self.assertIn(self.activity2, activities)
    
    def test_activities_page_no_activities(self):
        """Test activities page with destination having no activities."""
        destination_no_activities = Destination.objects.create(
            name='Empty Destination',
            country='Nowhere',
            description='No activities here',
            best_season='Never'
        )
        
        url = reverse('activities_page', kwargs={'destination_id': destination_no_activities.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['activities'].count(), 0)
    
    def test_activities_page_invalid_destination(self):
        """Test activities page with non-existent destination."""
        url = reverse('activities_page', kwargs={'destination_id': 999})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 404)


class TravelerProfileViewTest(TestCase):
    """Test cases for the traveler_profile view."""
    
    def setUp(self):
        """Set up test data and client."""
        self.client = Client()
        
        self.destination = Destination.objects.create(
            name='Sydney',
            country='Australia',
            description='Harbor city',
            best_season='Spring'
        )
        
        self.traveler = Traveler.objects.create(
            name='Sarah Connor',
            email='sarah@example.com',
            favorite_destination=self.destination
        )
        
        self.url = reverse('traveler_profile', kwargs={'traveler_id': self.traveler.id})
    
    def test_traveler_profile_view_get(self):
        """Test GET request to traveler profile."""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sarah Connor')
        self.assertContains(response, 'sarah@example.com')
        self.assertTemplateUsed(response, 'explorer/traveler_profile.html')
    
    def test_traveler_profile_context(self):
        """Test context data passed to template."""
        response = self.client.get(self.url)
        
        self.assertIn('traveler', response.context)
        self.assertEqual(response.context['traveler'], self.traveler)
    
    def test_traveler_profile_no_favorite_destination(self):
        """Test traveler profile with no favorite destination."""
        traveler_no_fav = Traveler.objects.create(
            name='John Doe',
            email='john@example.com'
        )
        
        url = reverse('traveler_profile', kwargs={'traveler_id': traveler_no_fav.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['traveler'].favorite_destination, None)
    
    def test_traveler_profile_invalid_traveler(self):
        """Test traveler profile with non-existent traveler."""
        url = reverse('traveler_profile', kwargs={'traveler_id': 999})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 404)


class ReviewsPageViewTest(TestCase):
    """Test cases for the reviews_page view."""
    
    def setUp(self):
        """Set up test data and client."""
        self.client = Client()
        
        self.destination = Destination.objects.create(
            name='Prague',
            country='Czech Republic',
            description='Medieval city',
            best_season='Spring'
        )
        
        self.traveler1 = Traveler.objects.create(
            name='Alice Wonder',
            email='alice@example.com'
        )
        self.traveler2 = Traveler.objects.create(
            name='Bob Builder',
            email='bob@example.com'
        )
        
        self.review1 = Review.objects.create(
            traveler=self.traveler1,
            destination=self.destination,
            rating=9,
            comment='Absolutely beautiful architecture!'
        )
        self.review2 = Review.objects.create(
            traveler=self.traveler2,
            destination=self.destination,
            rating=8,
            comment='Great beer and food.'
        )
        
        self.url = reverse('reviews_page', kwargs={'destination_id': self.destination.id})
    
    def test_reviews_page_view_get(self):
        """Test GET request to reviews page."""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Prague')
        self.assertContains(response, 'Alice Wonder')
        self.assertContains(response, 'Bob Builder')
        self.assertContains(response, 'Absolutely beautiful architecture!')
        self.assertContains(response, 'Great beer and food.')
        self.assertTemplateUsed(response, 'explorer/reviews.html')
    
    def test_reviews_page_context(self):
        """Test context data passed to template."""
        response = self.client.get(self.url)
        
        self.assertIn('destination', response.context)
        self.assertIn('reviews', response.context)
        
        self.assertEqual(response.context['destination'], self.destination)
        reviews = response.context['reviews']
        self.assertEqual(reviews.count(), 2)
        self.assertIn(self.review1, reviews)
        self.assertIn(self.review2, reviews)
    
    def test_reviews_page_no_reviews(self):
        """Test reviews page with destination having no reviews."""
        destination_no_reviews = Destination.objects.create(
            name='Lonely Place',
            country='Nowhere',
            description='No one has been here',
            best_season='Never'
        )
        
        url = reverse('reviews_page', kwargs={'destination_id': destination_no_reviews.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['reviews'].count(), 0)
    
    def test_reviews_page_invalid_destination(self):
        """Test reviews page with non-existent destination."""
        url = reverse('reviews_page', kwargs={'destination_id': 999})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 404)


class ViewsIntegrationTest(TestCase):
    """Integration tests for view workflows and interactions."""
    
    def setUp(self):
        """Set up comprehensive test data."""
        self.client = Client()
        
        # Create destinations
        self.destination1 = Destination.objects.create(
            name='Amsterdam',
            country='Netherlands',
            description='Canal city with rich history',
            best_season='Spring'
        )
        
        # Create activities
        self.activity = Activity.objects.create(
            name='Canal Cruise',
            destination=self.destination1,
            description='Scenic boat tour',
            cost_estimate=Decimal('18.50')
        )
        
        # Create travelers with user
        from django.contrib.auth.models import User
        self.user = User.objects.create_user(username='testuser', password='pass123')
        self.staff_user = User.objects.create_user(username='staff', password='staffpass', is_staff=True)
        
        self.traveler = Traveler.objects.create(
            name='Emma Travel',
            email='emma@example.com',
            favorite_destination=self.destination1,
            user=self.user
        )
        
        # Create reviews
        self.review = Review.objects.create(
            traveler=self.traveler,
            destination=self.destination1,
            rating=9,
            comment='Loved the canals and friendly people!'
        )
    
    def test_complete_user_workflow(self):
        """Test complete user workflow through the application."""
        # 1. Start at destination list
        response = self.client.get(reverse('destination_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Amsterdam')
        
        # 2. View activities for a destination
        response = self.client.get(
            reverse('activities_page', kwargs={'destination_id': self.destination1.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Canal Cruise')
        
        # 3. View reviews for the destination
        response = self.client.get(
            reverse('reviews_page', kwargs={'destination_id': self.destination1.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Emma Travel')
        self.assertContains(response, 'Loved the canals')
        
        # 4. View traveler profile
        response = self.client.get(
            reverse('traveler_profile', kwargs={'traveler_id': self.traveler.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Emma Travel')
        
        # 5. Create a new destination (need to be staff)
        self.client.login(username='staff', password='staffpass')
        new_destination_data = {
            'name': 'Vienna',
            'country': 'Austria',
            'description': 'Imperial city with beautiful architecture',
            'best_season': 'Fall'
        }
        response = self.client.post(reverse('destination_create'), new_destination_data)
        self.assertEqual(response.status_code, 302)
        
        # 6. Verify new destination appears in list
        response = self.client.get(reverse('destination_list'))
        self.assertContains(response, 'Vienna')
    
    def test_url_patterns_consistency(self):
        """Test that all URL patterns work correctly."""
        # Test destination list (root URL)
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        
        # Test activities URL pattern
        response = self.client.get(f'/destinations/{self.destination1.id}/activities/')
        self.assertEqual(response.status_code, 200)
        
        # Test reviews URL pattern
        response = self.client.get(f'/destinations/{self.destination1.id}/reviews/')
        self.assertEqual(response.status_code, 200)
        
        # Test traveler profile URL pattern
        response = self.client.get(f'/travelers/{self.traveler.id}/')
        self.assertEqual(response.status_code, 200)
        
        # Test destination create URL pattern (requires staff login)
        self.client.login(username='staff', password='staffpass')
        response = self.client.get('/destination/add/')
        self.assertEqual(response.status_code, 200)
    
    def test_navigation_links(self):
        """Test navigation links work correctly."""
        # Test that destination list contains proper links
        response = self.client.get(reverse('destination_list'))
        
        # Should contain links to activities and reviews
        self.assertContains(response, f'href="/destinations/{self.destination1.id}/activities/"')
        self.assertContains(response, f'href="/destinations/{self.destination1.id}/reviews/"')
    
    def test_error_handling(self):
        """Test error handling for edge cases."""
        # Test 404 for non-existent destination activities
        response = self.client.get('/destinations/999/activities/')
        self.assertEqual(response.status_code, 404)
        
        # Test 404 for non-existent destination reviews
        response = self.client.get('/destinations/999/reviews/')
        self.assertEqual(response.status_code, 404)
        
        # Test 404 for non-existent traveler
        response = self.client.get('/travelers/999/')
        self.assertEqual(response.status_code, 404)


class ViewSecurityTest(TestCase):
    """Test security aspects of views."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.destination = Destination.objects.create(
            name='Test Destination',
            country='Test Country',
            description='Test description',
            best_season='Test Season'
        )
    
    def test_csrf_protection(self):
        """Test CSRF protection on forms."""
        # Create staff user
        from django.contrib.auth.models import User
        staff_user = User.objects.create_user(username='staff', password='pass', is_staff=True)
        
        # Use a client with CSRF checks enabled
        from django.test import Client
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.login(username='staff', password='pass')
        
        # POST without CSRF token should fail with 403
        data = {
            'name': 'New Destination',
            'country': 'New Country',
            'description': 'New description',
            'best_season': 'New Season'
        }
        
        response = csrf_client.post(reverse('destination_create'), data)
        # Should be rejected with 403 Forbidden
        self.assertEqual(response.status_code, 403)
    
    def test_sql_injection_protection(self):
        """Test protection against SQL injection attempts."""
        # Try SQL injection in URL parameters
        malicious_id = "1; DROP TABLE explorer_destination; --"
        
        # This should safely return 404, not execute SQL
        response = self.client.get(f'/destinations/{malicious_id}/activities/')
        self.assertEqual(response.status_code, 404)
    
    def test_xss_protection(self):
        """Test XSS protection in form inputs."""
        # Create staff user
        from django.contrib.auth.models import User
        staff_user = User.objects.create_user(username='staff', password='pass', is_staff=True)
        self.client.login(username='staff', password='pass')
        
        xss_payload = '<script>alert("XSS")</script>'
        
        data = {
            'name': xss_payload,
            'country': 'Test Country',
            'description': 'Test description',
            'best_season': 'Test Season'
        }
        
        response = self.client.post(reverse('destination_create'), data)
        
        if response.status_code == 302:  # Successfully created
            # Check that the script tag is escaped in the display
            destination = Destination.objects.get(name=xss_payload)
            list_response = self.client.get(reverse('destination_list'))
            # Django templates should auto-escape the content
            self.assertNotContains(list_response, '<script>alert("XSS")</script>')
            self.assertContains(list_response, '&lt;script&gt;')  # Escaped version