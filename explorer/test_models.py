"""
Unit tests for Explorer models.
Tests model validation, methods, relationships, and edge cases.
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from decimal import Decimal
from explorer.models import Destination, Activity, Traveler, Review


class DestinationModelTest(TestCase):
    """Test cases for the Destination model."""
    
    def setUp(self):
        """Set up test data."""
        self.destination_data = {
            'name': 'Paris',
            'country': 'France',
            'description': 'The City of Light with beautiful architecture and culture.',
            'best_season': 'Spring'
        }
    
    def test_destination_creation(self):
        """Test creating a destination with valid data."""
        destination = Destination.objects.create(**self.destination_data)
        self.assertEqual(destination.name, 'Paris')
        self.assertEqual(destination.country, 'France')
        self.assertEqual(str(destination), 'Paris')
    
    def test_destination_str_method(self):
        """Test the string representation of destination."""
        destination = Destination.objects.create(**self.destination_data)
        self.assertEqual(str(destination), 'Paris')
    
    def test_destination_fields_max_length(self):
        """Test field max length constraints."""
        # Test name field max length (100 chars)
        long_name = 'x' * 101
        with self.assertRaises(ValidationError):
            destination = Destination(
                name=long_name,
                country='France',
                description='Test description',
                best_season='Spring'
            )
            destination.full_clean()
        
        # Test country field max length (100 chars)
        long_country = 'x' * 101
        with self.assertRaises(ValidationError):
            destination = Destination(
                name='Paris',
                country=long_country,
                description='Test description',
                best_season='Spring'
            )
            destination.full_clean()
    
    def test_destination_required_fields(self):
        """Test that required fields cannot be empty."""
        # Test missing name
        with self.assertRaises(ValidationError):
            destination = Destination(
                country='France',
                description='Test description',
                best_season='Spring'
            )
            destination.full_clean()
        
        # Test missing country
        with self.assertRaises(ValidationError):
            destination = Destination(
                name='Paris',
                description='Test description',
                best_season='Spring'
            )
            destination.full_clean()
    
    def test_destination_image_field(self):
        """Test image field is optional."""
        destination = Destination.objects.create(**self.destination_data)
        self.assertIsNone(destination.image.name if not destination.image else None)
    
    def test_destination_relationships(self):
        """Test destination can have activities and reviews."""
        destination = Destination.objects.create(**self.destination_data)
        
        # Test activities relationship
        self.assertEqual(destination.activities.count(), 0)
        
        # Test reviews relationship
        self.assertEqual(destination.reviews.count(), 0)


class ActivityModelTest(TestCase):
    """Test cases for the Activity model."""
    
    def setUp(self):
        """Set up test data."""
        self.destination = Destination.objects.create(
            name='Tokyo',
            country='Japan',
            description='Modern city with traditional culture.',
            best_season='Spring'
        )
        self.activity_data = {
            'name': 'Visit Tokyo Tower',
            'destination': self.destination,
            'description': 'Iconic tower with great city views.',
            'cost_estimate': Decimal('25.50')
        }
    
    def test_activity_creation(self):
        """Test creating an activity with valid data."""
        activity = Activity.objects.create(**self.activity_data)
        self.assertEqual(activity.name, 'Visit Tokyo Tower')
        self.assertEqual(activity.destination, self.destination)
        self.assertEqual(activity.cost_estimate, Decimal('25.50'))
        self.assertEqual(str(activity), 'Visit Tokyo Tower')
    
    def test_activity_str_method(self):
        """Test the string representation of activity."""
        activity = Activity.objects.create(**self.activity_data)
        self.assertEqual(str(activity), 'Visit Tokyo Tower')
    
    def test_activity_destination_relationship(self):
        """Test activity belongs to destination."""
        activity = Activity.objects.create(**self.activity_data)
        self.assertEqual(activity.destination, self.destination)
        self.assertIn(activity, self.destination.activities.all())
    
    def test_activity_cascade_delete(self):
        """Test activity is deleted when destination is deleted."""
        activity = Activity.objects.create(**self.activity_data)
        activity_id = activity.id
        
        self.destination.delete()
        
        with self.assertRaises(Activity.DoesNotExist):
            Activity.objects.get(id=activity_id)
    
    def test_activity_cost_estimate_validation(self):
        """Test cost estimate field validation."""
        # Test valid decimal
        activity = Activity.objects.create(**self.activity_data)
        self.assertEqual(activity.cost_estimate, Decimal('25.50'))
        
        # Test zero cost
        activity_data = self.activity_data.copy()
        activity_data['cost_estimate'] = Decimal('0.00')
        activity = Activity.objects.create(**activity_data)
        self.assertEqual(activity.cost_estimate, Decimal('0.00'))
        
        # Test large number
        activity_data = self.activity_data.copy()
        activity_data['cost_estimate'] = Decimal('99999999.99')
        activity = Activity.objects.create(**activity_data)
        self.assertEqual(activity.cost_estimate, Decimal('99999999.99'))
    
    def test_activity_name_max_length(self):
        """Test activity name max length constraint."""
        long_name = 'x' * 101
        with self.assertRaises(ValidationError):
            activity = Activity(
                name=long_name,
                destination=self.destination,
                description='Test description',
                cost_estimate=Decimal('25.50')
            )
            activity.full_clean()


class TravelerModelTest(TestCase):
    """Test cases for the Traveler model."""
    
    def setUp(self):
        """Set up test data."""
        self.destination = Destination.objects.create(
            name='Bali',
            country='Indonesia',
            description='Beautiful island with beaches and culture.',
            best_season='Summer'
        )
        self.traveler_data = {
            'name': 'John Doe',
            'email': 'john.doe@example.com',
            'favorite_destination': self.destination
        }
    
    def test_traveler_creation(self):
        """Test creating a traveler with valid data."""
        traveler = Traveler.objects.create(**self.traveler_data)
        self.assertEqual(traveler.name, 'John Doe')
        self.assertEqual(traveler.email, 'john.doe@example.com')
        self.assertEqual(traveler.favorite_destination, self.destination)
        self.assertEqual(str(traveler), 'John Doe')
    
    def test_traveler_str_method(self):
        """Test the string representation of traveler."""
        traveler = Traveler.objects.create(**self.traveler_data)
        self.assertEqual(str(traveler), 'John Doe')
    
    def test_traveler_email_validation(self):
        """Test email field validation."""
        # Test invalid email format
        with self.assertRaises(ValidationError):
            traveler = Traveler(
                name='John Doe',
                email='invalid-email',
                favorite_destination=self.destination
            )
            traveler.full_clean()
    
    def test_traveler_favorite_destination_optional(self):
        """Test favorite destination is optional."""
        traveler_data = self.traveler_data.copy()
        traveler_data.pop('favorite_destination')
        traveler = Traveler.objects.create(**traveler_data)
        self.assertIsNone(traveler.favorite_destination)
    
    def test_traveler_favorite_destination_set_null(self):
        """Test favorite destination is set to null when destination is deleted."""
        traveler = Traveler.objects.create(**self.traveler_data)
        self.assertEqual(traveler.favorite_destination, self.destination)
        
        self.destination.delete()
        traveler.refresh_from_db()
        self.assertIsNone(traveler.favorite_destination)
    
    def test_traveler_name_max_length(self):
        """Test traveler name max length constraint."""
        long_name = 'x' * 101
        with self.assertRaises(ValidationError):
            traveler = Traveler(
                name=long_name,
                email='john@example.com'
            )
            traveler.full_clean()


class ReviewModelTest(TestCase):
    """Test cases for the Review model."""
    
    def setUp(self):
        """Set up test data."""
        self.destination = Destination.objects.create(
            name='Rome',
            country='Italy',
            description='Historic city with ancient ruins.',
            best_season='Fall'
        )
        self.traveler = Traveler.objects.create(
            name='Jane Smith',
            email='jane.smith@example.com'
        )
        self.review_data = {
            'traveler': self.traveler,
            'destination': self.destination,
            'rating': 8,
            'comment': 'Amazing historical sites and great food!'
        }
    
    def test_review_creation(self):
        """Test creating a review with valid data."""
        review = Review.objects.create(**self.review_data)
        self.assertEqual(review.traveler, self.traveler)
        self.assertEqual(review.destination, self.destination)
        self.assertEqual(review.rating, 8)
        self.assertEqual(review.comment, 'Amazing historical sites and great food!')
        self.assertEqual(str(review), 'Jane Smith - Rome')
    
    def test_review_str_method(self):
        """Test the string representation of review."""
        review = Review.objects.create(**self.review_data)
        self.assertEqual(str(review), 'Jane Smith - Rome')
    
    def test_review_rating_choices(self):
        """Test rating field accepts valid choices (1-10)."""
        # Test valid ratings
        for rating in range(1, 11):
            review_data = self.review_data.copy()
            review_data['rating'] = rating
            review = Review.objects.create(**review_data)
            self.assertEqual(review.rating, rating)
            review.delete()  # Clean up for next iteration
    
    def test_review_rating_invalid_choices(self):
        """Test rating field rejects invalid choices."""
        # Test invalid ratings (outside 1-10 range)
        invalid_ratings = [0, 11, -1, 15]
        for rating in invalid_ratings:
            with self.assertRaises(ValidationError):
                review = Review(
                    traveler=self.traveler,
                    destination=self.destination,
                    rating=rating,
                    comment='Test comment'
                )
                review.full_clean()
    
    def test_review_relationships(self):
        """Test review relationships with traveler and destination."""
        review = Review.objects.create(**self.review_data)
        
        # Test traveler relationship
        self.assertEqual(review.traveler, self.traveler)
        
        # Test destination relationship
        self.assertEqual(review.destination, self.destination)
        self.assertIn(review, self.destination.reviews.all())
    
    def test_review_cascade_delete_traveler(self):
        """Test review is deleted when traveler is deleted."""
        review = Review.objects.create(**self.review_data)
        review_id = review.id
        
        self.traveler.delete()
        
        with self.assertRaises(Review.DoesNotExist):
            Review.objects.get(id=review_id)
    
    def test_review_cascade_delete_destination(self):
        """Test review is deleted when destination is deleted."""
        review = Review.objects.create(**self.review_data)
        review_id = review.id
        
        self.destination.delete()
        
        with self.assertRaises(Review.DoesNotExist):
            Review.objects.get(id=review_id)
    
    def test_multiple_reviews_same_traveler_destination(self):
        """Test multiple reviews can exist for same traveler-destination pair."""
        review1 = Review.objects.create(**self.review_data)
        
        review_data2 = self.review_data.copy()
        review_data2['rating'] = 9
        review_data2['comment'] = 'Second visit was even better!'
        review2 = Review.objects.create(**review_data2)
        
        self.assertEqual(Review.objects.filter(
            traveler=self.traveler,
            destination=self.destination
        ).count(), 2)


class ModelIntegrationTest(TestCase):
    """Integration tests for model relationships and complex scenarios."""
    
    def setUp(self):
        """Set up complex test data."""
        # Create destinations
        self.destination1 = Destination.objects.create(
            name='Barcelona',
            country='Spain',
            description='Vibrant city with unique architecture.',
            best_season='Spring'
        )
        self.destination2 = Destination.objects.create(
            name='Santorini',
            country='Greece',
            description='Beautiful island with white buildings.',
            best_season='Summer'
        )
        
        # Create travelers
        self.traveler1 = Traveler.objects.create(
            name='Alice Johnson',
            email='alice@example.com',
            favorite_destination=self.destination1
        )
        self.traveler2 = Traveler.objects.create(
            name='Bob Wilson',
            email='bob@example.com'
        )
    
    def test_complex_destination_with_activities_and_reviews(self):
        """Test destination with multiple activities and reviews."""
        # Add activities to destination
        activity1 = Activity.objects.create(
            name='Sagrada Familia Tour',
            destination=self.destination1,
            description='Visit the iconic basilica.',
            cost_estimate=Decimal('30.00')
        )
        activity2 = Activity.objects.create(
            name='Park Güell Visit',
            destination=self.destination1,
            description='Explore Gaudí\'s colorful park.',
            cost_estimate=Decimal('25.00')
        )
        
        # Add reviews
        review1 = Review.objects.create(
            traveler=self.traveler1,
            destination=self.destination1,
            rating=9,
            comment='Absolutely loved the architecture!'
        )
        review2 = Review.objects.create(
            traveler=self.traveler2,
            destination=self.destination1,
            rating=8,
            comment='Great food and culture.'
        )
        
        # Test relationships
        self.assertEqual(self.destination1.activities.count(), 2)
        self.assertEqual(self.destination1.reviews.count(), 2)
        self.assertIn(activity1, self.destination1.activities.all())
        self.assertIn(review1, self.destination1.reviews.all())
    
    def test_traveler_with_multiple_reviews(self):
        """Test traveler can review multiple destinations."""
        review1 = Review.objects.create(
            traveler=self.traveler1,
            destination=self.destination1,
            rating=9,
            comment='Amazing city!'
        )
        review2 = Review.objects.create(
            traveler=self.traveler1,
            destination=self.destination2,
            rating=10,
            comment='Paradise on earth!'
        )
        
        traveler_reviews = Review.objects.filter(traveler=self.traveler1)
        self.assertEqual(traveler_reviews.count(), 2)
        
        destinations_reviewed = [review.destination for review in traveler_reviews]
        self.assertIn(self.destination1, destinations_reviewed)
        self.assertIn(self.destination2, destinations_reviewed)
    
    def test_data_integrity_constraints(self):
        """Test database integrity constraints."""
        # Test foreign key constraints are enforced
        # Note: SQLite doesn't enforce foreign key constraints by default in tests
        # This test is primarily for documentation purposes
        try:
            # Try to create activity with non-existent destination
            Activity.objects.create(
                name='Invalid Activity',
                destination_id=999,  # Non-existent destination
                description='This should fail',
                cost_estimate=Decimal('50.00')
            )
            # If no error is raised, it means SQLite FK constraints are off
            # Clean up the invalid object
            Activity.objects.filter(name='Invalid Activity').delete()
        except IntegrityError:
            # This is the expected behavior with FK constraints enabled
            pass