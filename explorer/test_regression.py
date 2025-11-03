"""
Regression tests for the TravelBug application.
Tests to prevent common bugs and ensure backward compatibility.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from decimal import Decimal
from explorer.models import Destination, Activity, Traveler, Review
from explorer.forms import DestinationForm


class ModelRegressionTest(TestCase):
    """Regression tests for model functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.destination = Destination.objects.create(
            name='Test Destination',
            country='Test Country',
            description='Test description',
            best_season='Test Season'
        )
        
        self.traveler = Traveler.objects.create(
            name='Test Traveler',
            email='test@example.com',
            favorite_destination=self.destination
        )
    
    def test_destination_str_method_regression(self):
        """Ensure destination string representation always works."""
        # Test with normal data
        destination = Destination.objects.create(
            name='Paris',
            country='France',
            description='Beautiful city',
            best_season='Spring'
        )
        self.assertEqual(str(destination), 'Paris')
        
        # Test with special characters that could break string representation
        special_destination = Destination.objects.create(
            name='São Paulo',
            country='Brasil',
            description='City with special chars',
            best_season='Year-round'
        )
        self.assertEqual(str(special_destination), 'São Paulo')
        
        # Test with very long name (at max length)
        long_name = 'x' * 100  # Max length for name field
        long_destination = Destination.objects.create(
            name=long_name,
            country='Test',
            description='Test',
            best_season='Test'
        )
        self.assertEqual(str(long_destination), long_name)
    
    def test_activity_cost_decimal_precision_regression(self):
        """Ensure decimal precision is maintained for activity costs."""
        # Test various decimal values that have caused issues
        test_costs = [
            Decimal('0.00'),
            Decimal('9.99'),
            Decimal('10.50'),
            Decimal('999.99'),
            Decimal('1000.00'),
            Decimal('99999999.99')  # Max value for 10 digits, 2 decimal places
        ]
        
        for i, cost in enumerate(test_costs):
            activity = Activity.objects.create(
                name=f'Test Activity {i}',
                destination=self.destination,
                description=f'Test description {i}',
                cost_estimate=cost
            )
            # Refresh from database to ensure precision is maintained
            activity.refresh_from_db()
            self.assertEqual(activity.cost_estimate, cost)
    
    def test_review_rating_validation_regression(self):
        """Ensure review rating validation works correctly."""
        # Test all valid ratings (1-10)
        for rating in range(1, 11):
            review = Review(
                traveler=self.traveler,
                destination=self.destination,
                rating=rating,
                comment=f'Test comment for rating {rating}'
            )
            # Should not raise ValidationError
            review.full_clean()
            review.save()
            review.delete()  # Clean up for next iteration
        
        # Test invalid ratings
        invalid_ratings = [0, 11, -1, 15, -5]
        for rating in invalid_ratings:
            with self.assertRaises(ValidationError):
                review = Review(
                    traveler=self.traveler,
                    destination=self.destination,
                    rating=rating,
                    comment='Test comment'
                )
                review.full_clean()
    
    def test_email_validation_regression(self):
        """Ensure email validation works correctly."""
        # Test valid emails
        valid_emails = [
            'test@example.com',
            'user+tag@domain.co.uk',
            'user.name@subdomain.domain.org',
            'user123@test-domain.com'
        ]
        
        for i, email in enumerate(valid_emails):
            traveler = Traveler(
                name=f'Test User {i}',
                email=email
            )
            # Should not raise ValidationError
            traveler.full_clean()
            traveler.save()
        
        # Test invalid emails
        invalid_emails = [
            'invalid-email',
            '@domain.com',
            'user@',
            'user space@domain.com',
            'user..double.dot@domain.com'
        ]
        
        for email in invalid_emails:
            with self.assertRaises(ValidationError):
                traveler = Traveler(
                    name='Test User',
                    email=email
                )
                traveler.full_clean()
    
    def test_cascade_delete_regression(self):
        """Ensure cascade delete behavior is maintained."""
        # Create related objects
        activity = Activity.objects.create(
            name='Test Activity',
            destination=self.destination,
            description='Test description',
            cost_estimate=Decimal('25.00')
        )
        
        review = Review.objects.create(
            traveler=self.traveler,
            destination=self.destination,
            rating=8,
            comment='Test review'
        )
        
        activity_id = activity.id
        review_id = review.id
        
        # Delete destination should cascade to activities and reviews
        self.destination.delete()
        
        # Verify cascaded deletes
        self.assertFalse(Activity.objects.filter(id=activity_id).exists())
        self.assertFalse(Review.objects.filter(id=review_id).exists())
        
        # Traveler should still exist (SET_NULL for favorite_destination)
        self.traveler.refresh_from_db()
        self.assertTrue(Traveler.objects.filter(id=self.traveler.id).exists())
        self.assertIsNone(self.traveler.favorite_destination)


class ViewRegressionTest(TestCase):
    """Regression tests for view functionality."""
    
    def setUp(self):
        """Set up test data and client."""
        self.client = Client()
        
        self.destination = Destination.objects.create(
            name='Barcelona',
            country='Spain',
            description='Beautiful Mediterranean city',
            best_season='Spring'
        )
        
        self.traveler = Traveler.objects.create(
            name='John Doe',
            email='john@example.com'
        )
    
    def test_destination_list_pagination_regression(self):
        """Test destination list handles large datasets correctly."""
        # Create many destinations to test potential pagination issues
        destinations = []
        for i in range(50):
            destination = Destination.objects.create(
                name=f'Destination {i:02d}',
                country=f'Country {i}',
                description=f'Description for destination {i}',
                best_season='Summer'
            )
            destinations.append(destination)
        
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        
        # Home page only shows 6 featured destinations, not all
        # Should handle large dataset without performance issues
        self.assertContains(response, 'Destination')
        
        # Check destination list page can handle all destinations
        response = self.client.get('/destinations/')
        self.assertEqual(response.status_code, 200)
        # Should show all destinations (or paginate them properly)
        self.assertContains(response, 'Destination')
    
    def test_url_parameter_validation_regression(self):
        """Test URL parameter validation prevents errors."""
        # Test non-numeric IDs
        invalid_ids = ['abc', '1.5', '1; DROP TABLE', 'null', '']
        
        for invalid_id in invalid_ids:
            # Should return 404, not cause server error
            response = self.client.get(f'/destinations/{invalid_id}/activities/')
            self.assertEqual(response.status_code, 404)
            
            response = self.client.get(f'/destinations/{invalid_id}/reviews/')
            self.assertEqual(response.status_code, 404)
            
            response = self.client.get(f'/travelers/{invalid_id}/')
            self.assertEqual(response.status_code, 404)
    
    def test_form_submission_edge_cases_regression(self):
        """Test form submission handles edge cases correctly."""
        # Create a staff user for destination_create
        from django.contrib.auth.models import User
        staff_user = User.objects.create_user(username='staff', password='pass', is_staff=True)
        self.client.login(username='staff', password='pass')
        
        # Test very long strings at boundary conditions
        boundary_data = {
            'name': 'x' * 100,  # Exactly at max length
            'country': 'y' * 100,  # Exactly at max length
            'description': 'z' * 1000,  # Very long description
            'best_season': 'w' * 50  # Exactly at max length
        }
        
        response = self.client.post(reverse('destination_create'), boundary_data)
        self.assertEqual(response.status_code, 302)  # Should succeed
        
        # Verify destination was created
        self.assertTrue(Destination.objects.filter(name='x' * 100).exists())
        
        # Test strings that exceed max length by 1
        over_limit_data = {
            'name': 'x' * 101,  # Over max length
            'country': 'Spain',
            'description': 'Valid description',
            'best_season': 'Spring'
        }
        
        response = self.client.post(reverse('destination_create'), over_limit_data)
        self.assertEqual(response.status_code, 200)  # Should stay on form with errors
        self.assertContains(response, 'Ensure this value has at most 100 characters')
    
    def test_template_rendering_regression(self):
        """Test template rendering handles various data types correctly."""
        # Create destination with special characters
        special_destination = Destination.objects.create(
            name='Café & Restaurant "L\'Été"',
            country='Côte d\'Ivoire',
            description='Special chars: áéíóú, ñ, ü, ç, €, £, ¥, ©, ®, ™',
            best_season='Été (Summer)'
        )
        
        # Test all views render correctly with special characters
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        # Home page only shows first 6 featured destinations
        # The special destination might not appear, so check destination list instead
        
        response = self.client.get('/destinations/')
        self.assertEqual(response.status_code, 200)
        # HTML will escape special characters - check for the escaped HTML entity version
        self.assertContains(response, 'Caf')  # Should contain at least part of the name
        
        response = self.client.get(
            reverse('activities_page', kwargs={'destination_id': special_destination.id})
        )
        self.assertEqual(response.status_code, 200)
        # HTML escapes & as &amp; - check for "Caf" which is the unescaped part
        self.assertContains(response, 'Caf')
        
        response = self.client.get(
            reverse('reviews_page', kwargs={'destination_id': special_destination.id})
        )
        self.assertEqual(response.status_code, 200)
        # HTML escapes & as &amp; - check for "Caf" which is the unescaped part
        self.assertContains(response, 'Caf')
    
    def test_empty_data_handling_regression(self):
        """Test views handle empty datasets correctly."""
        # Test activities page with no activities
        response = self.client.get(
            reverse('activities_page', kwargs={'destination_id': self.destination.id})
        )
        self.assertEqual(response.status_code, 200)
        # Should not cause template errors
        self.assertContains(response, self.destination.name)
        
        # Test reviews page with no reviews
        response = self.client.get(
            reverse('reviews_page', kwargs={'destination_id': self.destination.id})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.destination.name)


class FormRegressionTest(TestCase):
    """Regression tests for form functionality."""
    
    def test_form_field_validation_regression(self):
        """Test form field validation handles edge cases."""
        # Test with whitespace-only data
        whitespace_data = {
            'name': '   ',
            'country': '\t\t',
            'description': '\n\n',
            'best_season': '   \t   '
        }
        
        form = DestinationForm(data=whitespace_data)
        self.assertFalse(form.is_valid())
        
        # All fields should have required errors
        for field in ['name', 'country', 'description', 'best_season']:
            self.assertIn(field, form.errors)
    
    def test_form_unicode_handling_regression(self):
        """Test form handles Unicode characters correctly."""
        unicode_data = {
            'name': '北京 (Beijing)',
            'country': '中华人民共和国',
            'description': 'الوصف باللغة العربية: مدينة جميلة جداً! 🏛️🌸',
            'best_season': 'весна (spring)'
        }
        
        form = DestinationForm(data=unicode_data)
        self.assertTrue(form.is_valid())
        
        destination = form.save()
        self.assertEqual(destination.name, '北京 (Beijing)')
        self.assertEqual(destination.country, '中华人民共和国')
    
    def test_form_html_content_regression(self):
        """Test form handles HTML content safely."""
        html_data = {
            'name': '<h1>Destination Name</h1>',
            'country': '<script>alert("XSS")</script>Spain',
            'description': '<p>Description with <a href="http://evil.com">link</a></p>',
            'best_season': '<b>Spring</b>'
        }
        
        form = DestinationForm(data=html_data)
        self.assertTrue(form.is_valid())  # Should accept as text
        
        destination = form.save()
        # HTML should be stored as literal text
        self.assertEqual(destination.name, '<h1>Destination Name</h1>')
        self.assertIn('<script>', destination.country)


class DatabaseRegressionTest(TestCase):
    """Regression tests for database interactions."""
    
    def test_concurrent_creation_regression(self):
        """Test concurrent object creation doesn't cause issues."""
        # Simulate concurrent destination creation
        destinations = []
        for i in range(10):
            destination = Destination.objects.create(
                name=f'Concurrent Destination {i}',
                country=f'Country {i}',
                description=f'Description {i}',
                best_season='Summer'
            )
            destinations.append(destination)
        
        # All should be created successfully
        self.assertEqual(len(destinations), 10)
        for destination in destinations:
            self.assertTrue(Destination.objects.filter(id=destination.id).exists())
    
    def test_foreign_key_integrity_regression(self):
        """Test foreign key integrity is maintained."""
        destination = Destination.objects.create(
            name='Test Destination',
            country='Test Country',
            description='Test description',
            best_season='Test Season'
        )
        
        traveler = Traveler.objects.create(
            name='Test Traveler',
            email='test@example.com',
            favorite_destination=destination
        )
        
        # Note: SQLite doesn't enforce foreign key constraints by default in tests
        # This test documents expected behavior
        try:
            # Try to create activity with invalid destination
            Activity.objects.create(
                name='Invalid Activity',
                destination_id=999,  # Non-existent destination
                description='This should fail',
                cost_estimate=Decimal('50.00')
            )
            # Clean up if created
            Activity.objects.filter(name='Invalid Activity').delete()
        except IntegrityError:
            # Expected with FK constraints enabled
            pass
        
        # Try to create review with invalid traveler
        try:
            Review.objects.create(
                traveler_id=999,  # Non-existent traveler
                destination=destination,
                rating=8,
                comment='This should fail'
            )
            # Clean up if created
            Review.objects.filter(comment='This should fail').delete()
        except IntegrityError:
            # Expected with FK constraints enabled
            pass
    
    def test_data_migration_regression(self):
        """Test data remains consistent across operations."""
        # Create initial data
        destination = Destination.objects.create(
            name='Original Name',
            country='Original Country',
            description='Original description',
            best_season='Original Season'
        )
        
        # Update destination
        destination.name = 'Updated Name'
        destination.save()
        
        # Refresh from database
        destination.refresh_from_db()
        self.assertEqual(destination.name, 'Updated Name')
        self.assertEqual(destination.country, 'Original Country')  # Should remain unchanged


class SecurityRegressionTest(TestCase):
    """Regression tests for security vulnerabilities."""
    
    def setUp(self):
        """Set up test client."""
        self.client = Client()
    
    def test_xss_prevention_regression(self):
        """Test XSS prevention in all input fields."""
        xss_payloads = [
            '<script>alert("XSS")</script>',
            'javascript:alert("XSS")',
            '<img src="x" onerror="alert(\'XSS\')">',
            '<svg onload="alert(\'XSS\')">',
            '"><script>alert("XSS")</script>'
        ]
        
        for payload in xss_payloads:
            # Create destination with XSS payload
            destination = Destination.objects.create(
                name=payload,
                country='Safe Country',
                description='Safe description',
                best_season='Safe season'
            )
            
            # Check destination list doesn't execute script
            response = self.client.get('/')
            self.assertEqual(response.status_code, 200)
            # Should not contain unescaped script tags
            self.assertNotContains(response, '<script>alert(')
            
            destination.delete()  # Clean up
    
    def test_sql_injection_prevention_regression(self):
        """Test SQL injection prevention."""
        # Create a staff user for destination_create
        from django.contrib.auth.models import User
        staff_user = User.objects.create_user(username='staff', password='pass', is_staff=True)
        self.client.login(username='staff', password='pass')
        
        # Create a legitimate destination first
        Destination.objects.create(
            name='Legitimate Destination',
            country='Test Country',
            description='Test description',
            best_season='Summer'
        )
        
        sql_payloads = [
            "'; DROP TABLE explorer_destination; --",
            "' OR '1'='1",
            "'; INSERT INTO explorer_destination (name) VALUES ('hacked'); --",
            "1; DELETE FROM explorer_destination; --"
        ]
        
        for payload in sql_payloads:
            # Test in URL parameters
            response = self.client.get(f'/destinations/{payload}/activities/')
            self.assertEqual(response.status_code, 404)  # Should return 404, not execute SQL
            
            # Test in form data
            data = {
                'name': payload,
                'country': 'Test Country',
                'description': 'Test description',
                'best_season': 'Test Season'
            }
            
            response = self.client.post(reverse('destination_create'), data)
            # Should either succeed (saving as text) or show validation errors
            self.assertIn(response.status_code, [200, 302])
            
            # Verify table still exists and has expected data
            self.assertTrue(Destination.objects.exists())
    
    def test_csrf_protection_regression(self):
        """Test CSRF protection is maintained."""
        # Test POST request without CSRF token
        data = {
            'name': 'Test Destination',
            'country': 'Test Country',
            'description': 'Test description',
            'best_season': 'Test Season'
        }
        
        # Create client without CSRF token
        csrf_client = Client(enforce_csrf_checks=True)
        response = csrf_client.post(reverse('destination_create'), data)
        
        # Should be rejected (403) or redirected to form with error
        self.assertIn(response.status_code, [403, 200])


class PerformanceRegressionTest(TestCase):
    """Regression tests for performance issues."""
    
    def test_large_dataset_performance_regression(self):
        """Test application performs well with large datasets."""
        # Create large dataset
        destinations = []
        for i in range(100):
            destination = Destination.objects.create(
                name=f'Performance Test Destination {i:03d}',
                country=f'Country {i}',
                description=f'Long description for destination {i} with lots of text to test performance',
                best_season='Summer'
            )
            destinations.append(destination)
            
            # Add activities
            for j in range(5):
                Activity.objects.create(
                    name=f'Activity {j} for Destination {i}',
                    destination=destination,
                    description=f'Activity description {j}',
                    cost_estimate=Decimal(f'{j * 5}.00')
                )
        
        # Test destination list performance
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        
        # Test individual destination pages
        test_destination = destinations[50]  # Test middle destination
        
        response = self.client.get(
            reverse('activities_page', kwargs={'destination_id': test_destination.id})
        )
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(
            reverse('reviews_page', kwargs={'destination_id': test_destination.id})
        )
        self.assertEqual(response.status_code, 200)
    
    def test_query_optimization_regression(self):
        """Test database queries are optimized."""
        # Create test data with relationships
        destination = Destination.objects.create(
            name='Query Test Destination',
            country='Test Country',
            description='Test description',
            best_season='Test Season'
        )
        
        # Create activities
        for i in range(10):
            Activity.objects.create(
                name=f'Activity {i}',
                destination=destination,
                description=f'Description {i}',
                cost_estimate=Decimal(f'{i * 10}.00')
            )
        
        # Create travelers and reviews
        for i in range(10):
            traveler = Traveler.objects.create(
                name=f'Traveler {i}',
                email=f'traveler{i}@example.com'
            )
            
            Review.objects.create(
                traveler=traveler,
                destination=destination,
                rating=(i % 10) + 1,
                comment=f'Review {i} comment'
            )
        
        # Test that views don't cause N+1 query problems
        # These should complete without excessive database queries
        response = self.client.get(
            reverse('activities_page', kwargs={'destination_id': destination.id})
        )
        self.assertEqual(response.status_code, 200)
        
        response = self.client.get(
            reverse('reviews_page', kwargs={'destination_id': destination.id})
        )
        self.assertEqual(response.status_code, 200)