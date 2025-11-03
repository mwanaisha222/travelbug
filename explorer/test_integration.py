"""
Integration tests for the TravelBug application.
Tests end-to-end workflows, user interactions, and system integration.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from decimal import Decimal
from explorer.models import Destination, Activity, Traveler, Review


class UserWorkflowIntegrationTest(TestCase):
    """Test complete user workflows through the application."""
    
    def setUp(self):
        """Set up test data and client."""
        self.client = Client()
        
        # Create comprehensive test data
        self.destination1 = Destination.objects.create(
            name='Paris',
            country='France',
            description='The City of Light with beautiful architecture and rich culture.',
            best_season='Spring'
        )
        
        self.destination2 = Destination.objects.create(
            name='Tokyo',
            country='Japan',
            description='Modern metropolis blending tradition and innovation.',
            best_season='Cherry blossom season'
        )
        
        # Create activities
        self.activity1 = Activity.objects.create(
            name='Eiffel Tower Visit',
            destination=self.destination1,
            description='Iconic tower with panoramic city views.',
            cost_estimate=Decimal('25.00')
        )
        
        self.activity2 = Activity.objects.create(
            name='Louvre Museum',
            destination=self.destination1,
            description='World\'s largest art museum.',
            cost_estimate=Decimal('17.00')
        )
        
        self.activity3 = Activity.objects.create(
            name='Senso-ji Temple',
            destination=self.destination2,
            description='Ancient Buddhist temple in Asakusa.',
            cost_estimate=Decimal('0.00')
        )
        
        # Create travelers
        self.traveler1 = Traveler.objects.create(
            name='Emma Explorer',
            email='emma@explorer.com',
            favorite_destination=self.destination1
        )
        
        self.traveler2 = Traveler.objects.create(
            name='James Journey',
            email='james@journey.com',
            favorite_destination=self.destination2
        )
        
        # Create reviews
        self.review1 = Review.objects.create(
            traveler=self.traveler1,
            destination=self.destination1,
            rating=9,
            comment='Absolutely magical city! The architecture is breathtaking.'
        )
        
        self.review2 = Review.objects.create(
            traveler=self.traveler2,
            destination=self.destination1,
            rating=8,
            comment='Great food and culture, but very crowded.'
        )
        
        self.review3 = Review.objects.create(
            traveler=self.traveler1,
            destination=self.destination2,
            rating=10,
            comment='Amazing blend of traditional and modern culture!'
        )
    
    def test_complete_discovery_workflow(self):
        """Test complete user discovery workflow."""
        # Step 1: User lands on homepage (destination list)
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'TravelBucket')
        self.assertContains(response, 'Paris')
        self.assertContains(response, 'Tokyo')
        
        # Step 2: User clicks on activities for Paris
        response = self.client.get(reverse('activities_page', kwargs={'destination_id': self.destination1.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Paris')
        self.assertContains(response, 'Eiffel Tower Visit')
        self.assertContains(response, 'Louvre Museum')
        self.assertContains(response, '25.00')  # Cost estimate
        
        # Step 3: User checks reviews for Paris
        response = self.client.get(reverse('reviews_page', kwargs={'destination_id': self.destination1.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Paris')
        self.assertContains(response, 'Emma Explorer')
        self.assertContains(response, 'James Journey')
        self.assertContains(response, 'Absolutely magical city!')
        self.assertContains(response, 'Great food and culture')
        
        # Step 4: User explores traveler profile
        response = self.client.get(reverse('traveler_profile', kwargs={'traveler_id': self.traveler1.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Emma Explorer')
        self.assertContains(response, 'emma@explorer.com')
        
        # Step 5: User explores second destination
        response = self.client.get(reverse('activities_page', kwargs={'destination_id': self.destination2.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Tokyo')
        self.assertContains(response, 'Senso-ji Temple')
        self.assertContains(response, '0.00')  # Free activity
    
    def test_destination_creation_workflow(self):
        """Test complete destination creation workflow."""
        # Step 1: User goes to destination list
        response = self.client.get('/')
        initial_count = Destination.objects.count()
        
        # Step 2: User navigates to create destination form
        response = self.client.get(reverse('destination_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Destination Name')
        self.assertContains(response, 'Country')
        
        # Step 3: User fills out and submits form
        new_destination_data = {
            'name': 'Rome',
            'country': 'Italy',
            'description': 'Historic city with ancient ruins and incredible cuisine.',
            'best_season': 'Fall'
        }
        response = self.client.post(reverse('destination_create'), new_destination_data)
        
        # Step 4: User is redirected to destination list
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('destination_list'))
        
        # Step 5: Verify new destination appears in list
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Rome')
        self.assertContains(response, 'Italy')
        
        # Verify destination count increased
        self.assertEqual(Destination.objects.count(), initial_count + 1)
        
        # Step 6: User can view new destination's activities page (empty)
        new_destination = Destination.objects.get(name='Rome')
        response = self.client.get(reverse('activities_page', kwargs={'destination_id': new_destination.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Rome')
    
    def test_navigation_consistency_workflow(self):
        """Test consistent navigation throughout the application."""
        # Start from home page
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        
        # Navigate to activities
        response = self.client.get(reverse('activities_page', kwargs={'destination_id': self.destination1.id}))
        self.assertEqual(response.status_code, 200)
        
        # Check if we can navigate back to home from activities page
        self.assertContains(response, 'TravelBucket')  # Should have navigation link
        
        # Navigate to reviews
        response = self.client.get(reverse('reviews_page', kwargs={'destination_id': self.destination1.id}))
        self.assertEqual(response.status_code, 200)
        
        # Navigate to traveler profile
        response = self.client.get(reverse('traveler_profile', kwargs={'traveler_id': self.traveler1.id}))
        self.assertEqual(response.status_code, 200)
        
        # Navigate to destination creation
        response = self.client.get(reverse('destination_create'))
        self.assertEqual(response.status_code, 200)
        
        # All pages should be accessible without errors
    
    def test_data_consistency_across_views(self):
        """Test that data remains consistent across different views."""
        # Check destination data consistency
        destination_id = self.destination1.id
        
        # In destination list
        response = self.client.get('/')
        self.assertContains(response, 'Paris')
        self.assertContains(response, 'France')
        
        # In activities page
        response = self.client.get(reverse('activities_page', kwargs={'destination_id': destination_id}))
        self.assertContains(response, 'Paris')  # Same destination name
        
        # In reviews page
        response = self.client.get(reverse('reviews_page', kwargs={'destination_id': destination_id}))
        self.assertContains(response, 'Paris')  # Same destination name
        
        # Check traveler data consistency
        traveler_id = self.traveler1.id
        
        # In traveler profile
        response = self.client.get(reverse('traveler_profile', kwargs={'traveler_id': traveler_id}))
        self.assertContains(response, 'Emma Explorer')
        self.assertContains(response, 'emma@explorer.com')
        
        # In reviews (should show same traveler name)
        response = self.client.get(reverse('reviews_page', kwargs={'destination_id': destination_id}))
        self.assertContains(response, 'Emma Explorer')  # Same traveler name
    
    def test_error_handling_workflow(self):
        """Test error handling in complete workflows."""
        # Test 404 error handling
        response = self.client.get('/destinations/999/activities/')
        self.assertEqual(response.status_code, 404)
        
        response = self.client.get('/destinations/999/reviews/')
        self.assertEqual(response.status_code, 404)
        
        response = self.client.get('/travelers/999/')
        self.assertEqual(response.status_code, 404)
        
        # Test form validation error handling
        invalid_data = {
            'name': '',  # Required field
            'country': 'Italy',
            'description': 'Test',
            'best_season': 'Fall'
        }
        response = self.client.post(reverse('destination_create'), invalid_data)
        self.assertEqual(response.status_code, 200)  # Should stay on form page
        self.assertContains(response, 'This field is required')


class DataIntegrityIntegrationTest(TestCase):
    """Test data integrity across the application."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        
        self.destination = Destination.objects.create(
            name='Barcelona',
            country='Spain',
            description='Vibrant city with unique architecture.',
            best_season='Spring'
        )
        
        self.traveler = Traveler.objects.create(
            name='Maria Santos',
            email='maria@example.com',
            favorite_destination=self.destination
        )
        
        self.activity = Activity.objects.create(
            name='Sagrada Familia',
            destination=self.destination,
            description='Gaudí\'s masterpiece.',
            cost_estimate=Decimal('30.00')
        )
        
        self.review = Review.objects.create(
            traveler=self.traveler,
            destination=self.destination,
            rating=9,
            comment='Incredible architecture!'
        )
    
    def test_cascade_delete_integrity(self):
        """Test that cascade deletes work correctly across views."""
        destination_id = self.destination.id
        activity_id = self.activity.id
        review_id = self.review.id
        
        # Verify all related objects exist
        self.assertTrue(Activity.objects.filter(id=activity_id).exists())
        self.assertTrue(Review.objects.filter(id=review_id).exists())
        
        # Delete destination
        self.destination.delete()
        
        # Verify cascade deletes worked
        self.assertFalse(Activity.objects.filter(id=activity_id).exists())
        self.assertFalse(Review.objects.filter(id=review_id).exists())
        
        # Verify 404 responses for deleted destination
        response = self.client.get(f'/destinations/{destination_id}/activities/')
        self.assertEqual(response.status_code, 404)
        
        response = self.client.get(f'/destinations/{destination_id}/reviews/')
        self.assertEqual(response.status_code, 404)
    
    def test_favorite_destination_null_handling(self):
        """Test handling when favorite destination is deleted."""
        traveler_id = self.traveler.id
        
        # Verify traveler has favorite destination
        response = self.client.get(reverse('traveler_profile', kwargs={'traveler_id': traveler_id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Barcelona')  # Favorite destination
        
        # Delete the favorite destination
        self.destination.delete()
        
        # Refresh traveler from database
        self.traveler.refresh_from_db()
        self.assertIsNone(self.traveler.favorite_destination)
        
        # Traveler profile should still work
        response = self.client.get(reverse('traveler_profile', kwargs={'traveler_id': traveler_id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Maria Santos')
    
    def test_multiple_reviews_integrity(self):
        """Test multiple reviews for same destination work correctly."""
        # Create another traveler and review
        traveler2 = Traveler.objects.create(
            name='Carlos Rodriguez',
            email='carlos@example.com'
        )
        
        review2 = Review.objects.create(
            traveler=traveler2,
            destination=self.destination,
            rating=8,
            comment='Beautiful city, great food!'
        )
        
        # Check reviews page shows both reviews
        response = self.client.get(reverse('reviews_page', kwargs={'destination_id': self.destination.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Maria Santos')
        self.assertContains(response, 'Carlos Rodriguez')
        self.assertContains(response, 'Incredible architecture!')
        self.assertContains(response, 'Beautiful city, great food!')


class PerformanceIntegrationTest(TestCase):
    """Test performance aspects of the application."""
    
    def setUp(self):
        """Set up large dataset for performance testing."""
        self.client = Client()
        
        # Create multiple destinations
        self.destinations = []
        for i in range(10):
            destination = Destination.objects.create(
                name=f'Destination {i}',
                country=f'Country {i}',
                description=f'Description for destination {i}',
                best_season='Summer'
            )
            self.destinations.append(destination)
            
            # Create activities for each destination
            for j in range(5):
                Activity.objects.create(
                    name=f'Activity {j} in {destination.name}',
                    destination=destination,
                    description=f'Activity description {j}',
                    cost_estimate=Decimal(f'{j * 10}.00')
                )
        
        # Create travelers
        self.travelers = []
        for i in range(20):
            traveler = Traveler.objects.create(
                name=f'Traveler {i}',
                email=f'traveler{i}@example.com',
                favorite_destination=self.destinations[i % len(self.destinations)]
            )
            self.travelers.append(traveler)
            
            # Create reviews
            for j in range(3):
                Review.objects.create(
                    traveler=traveler,
                    destination=self.destinations[j % len(self.destinations)],
                    rating=(j % 10) + 1,
                    comment=f'Review {j} by {traveler.name}'
                )
    
    def test_destination_list_performance(self):
        """Test destination list page performance with many destinations."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        
        # Should show all destinations
        for destination in self.destinations:
            self.assertContains(response, destination.name)
    
    def test_activities_page_performance(self):
        """Test activities page performance with many activities."""
        destination = self.destinations[0]
        response = self.client.get(reverse('activities_page', kwargs={'destination_id': destination.id}))
        self.assertEqual(response.status_code, 200)
        
        # Should show all activities for the destination
        activities = destination.activities.all()
        for activity in activities:
            self.assertContains(response, activity.name)
    
    def test_reviews_page_performance(self):
        """Test reviews page performance with many reviews."""
        destination = self.destinations[0]
        response = self.client.get(reverse('reviews_page', kwargs={'destination_id': destination.id}))
        self.assertEqual(response.status_code, 200)
        
        # Should show all reviews for the destination
        reviews = destination.reviews.all()
        for review in reviews:
            self.assertContains(response, review.traveler.name)


class SecurityIntegrationTest(TestCase):
    """Test security aspects across the application."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        
        self.destination = Destination.objects.create(
            name='Test Destination',
            country='Test Country',
            description='Test description',
            best_season='Test Season'
        )
    
    def test_xss_protection_across_views(self):
        """Test XSS protection across different views."""
        # Create destination with XSS payload
        xss_payload = '<script>alert("XSS")</script>'
        xss_destination = Destination.objects.create(
            name=xss_payload,
            country='Safe Country',
            description='Safe description',
            best_season='Safe season'
        )
        
        # Test destination list
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        # Should not contain unescaped script tag
        self.assertNotContains(response, '<script>alert("XSS")</script>')
        
        # Test activities page
        response = self.client.get(reverse('activities_page', kwargs={'destination_id': xss_destination.id}))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, '<script>alert("XSS")</script>')
        
        # Test reviews page
        response = self.client.get(reverse('reviews_page', kwargs={'destination_id': xss_destination.id}))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, '<script>alert("XSS")</script>')
    
    def test_sql_injection_protection(self):
        """Test SQL injection protection in URL parameters."""
        # Test malicious destination ID
        malicious_id = "1'; DROP TABLE explorer_destination; --"
        
        response = self.client.get(f'/destinations/{malicious_id}/activities/')
        self.assertEqual(response.status_code, 404)  # Should return 404, not execute SQL
        
        # Verify table still exists
        self.assertTrue(Destination.objects.filter(id=self.destination.id).exists())
    
    def test_file_upload_security(self):
        """Test file upload security in destination creation."""
        # Test with potentially malicious filename
        malicious_file = SimpleUploadedFile(
            name='../../etc/passwd',
            content=b'malicious content',
            content_type='text/plain'
        )
        
        data = {
            'name': 'Test Destination',
            'country': 'Test Country',
            'description': 'Test description',
            'best_season': 'Test Season'
        }
        
        response = self.client.post(
            reverse('destination_create'),
            data,
            files={'image': malicious_file}
        )
        
        # Should handle malicious filename safely
        # The exact behavior depends on Django settings and validators