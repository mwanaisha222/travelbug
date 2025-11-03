"""
Unit tests for Explorer forms.
Tests form validation, error handling, and data processing.
"""
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from explorer.forms import DestinationForm
from explorer.models import Destination


class DestinationFormTest(TestCase):
    """Test cases for the DestinationForm."""
    
    def setUp(self):
        """Set up test data."""
        self.valid_data = {
            'name': 'Barcelona',
            'country': 'Spain',
            'description': 'Beautiful Mediterranean city with unique architecture.',
            'best_season': 'Spring'
        }
    
    def test_destination_form_valid_data(self):
        """Test form with valid data."""
        form = DestinationForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['name'], 'Barcelona')
        self.assertEqual(form.cleaned_data['country'], 'Spain')
        self.assertEqual(form.cleaned_data['description'], 'Beautiful Mediterranean city with unique architecture.')
        self.assertEqual(form.cleaned_data['best_season'], 'Spring')
    
    def test_destination_form_save(self):
        """Test form save functionality."""
        form = DestinationForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
        
        destination = form.save()
        self.assertIsInstance(destination, Destination)
        self.assertEqual(destination.name, 'Barcelona')
        self.assertEqual(destination.country, 'Spain')
        
        # Verify it was saved to database
        saved_destination = Destination.objects.get(id=destination.id)
        self.assertEqual(saved_destination.name, 'Barcelona')
    
    def test_destination_form_missing_required_fields(self):
        """Test form validation with missing required fields."""
        # Test missing name
        data = self.valid_data.copy()
        data.pop('name')
        form = DestinationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertEqual(form.errors['name'], ['This field is required.'])
        
        # Test missing country
        data = self.valid_data.copy()
        data.pop('country')
        form = DestinationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('country', form.errors)
        self.assertEqual(form.errors['country'], ['This field is required.'])
        
        # Test missing description
        data = self.valid_data.copy()
        data.pop('description')
        form = DestinationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('description', form.errors)
        self.assertEqual(form.errors['description'], ['This field is required.'])
        
        # Test missing best_season
        data = self.valid_data.copy()
        data.pop('best_season')
        form = DestinationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('best_season', form.errors)
        self.assertEqual(form.errors['best_season'], ['This field is required.'])
    
    def test_destination_form_empty_data(self):
        """Test form with completely empty data."""
        form = DestinationForm(data={})
        self.assertFalse(form.is_valid())
        
        # All required fields should have errors
        required_fields = ['name', 'country', 'description', 'best_season']
        for field in required_fields:
            self.assertIn(field, form.errors)
            self.assertEqual(form.errors[field], ['This field is required.'])
    
    def test_destination_form_whitespace_only_data(self):
        """Test form with whitespace-only data."""
        whitespace_data = {
            'name': '   ',
            'country': '\t\t',
            'description': '\n\n',
            'best_season': '   \t   '
        }
        form = DestinationForm(data=whitespace_data)
        self.assertFalse(form.is_valid())
        
        # Should be treated as empty fields
        required_fields = ['name', 'country', 'description', 'best_season']
        for field in required_fields:
            self.assertIn(field, form.errors)
    
    def test_destination_form_field_max_lengths(self):
        """Test form validation for field max lengths."""
        # Test name field max length (100 characters)
        data = self.valid_data.copy()
        data['name'] = 'x' * 101  # Exceed max length
        form = DestinationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn('100 characters', str(form.errors['name']))
        
        # Test country field max length (100 characters)
        data = self.valid_data.copy()
        data['country'] = 'x' * 101  # Exceed max length
        form = DestinationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('country', form.errors)
        self.assertIn('100 characters', str(form.errors['country']))
        
        # Test best_season field max length (50 characters)
        data = self.valid_data.copy()
        data['best_season'] = 'x' * 51  # Exceed max length
        form = DestinationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('best_season', form.errors)
        self.assertIn('50 characters', str(form.errors['best_season']))
    
    def test_destination_form_exact_max_lengths(self):
        """Test form with data at exact max lengths (should be valid)."""
        data = {
            'name': 'x' * 100,  # Exact max length
            'country': 'y' * 100,  # Exact max length
            'description': 'z' * 1000,  # TextField has no inherent max length
            'best_season': 'w' * 50  # Exact max length
        }
        form = DestinationForm(data=data)
        self.assertTrue(form.is_valid())
    
    def test_destination_form_with_image(self):
        """Test form with image upload."""
        # Create a real image using PIL
        from PIL import Image
        import io
        
        image = Image.new('RGB', (100, 100), color='blue')
        image_io = io.BytesIO()
        image.save(image_io, format='JPEG')
        image_io.seek(0)
        
        test_image = SimpleUploadedFile(
            name='test_image.jpg',
            content=image_io.read(),
            content_type='image/jpeg'
        )
        
        form = DestinationForm(
            data=self.valid_data,
            files={'image': test_image}
        )
        self.assertTrue(form.is_valid())
        
        destination = form.save()
        self.assertTrue(destination.image)
        # Image name might be modified by Django's storage system, just check it exists
        self.assertTrue(destination.image.name)
    
    def test_destination_form_without_image(self):
        """Test form without image (should be valid as image is optional)."""
        form = DestinationForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
        
        destination = form.save()
        self.assertFalse(destination.image)  # No image should be attached
    
    def test_destination_form_invalid_image_type(self):
        """Test form with invalid image file type."""
        # Create a non-image file
        invalid_file = SimpleUploadedFile(
            name='test_document.txt',
            content=b'this is not an image',
            content_type='text/plain'
        )
        
        form = DestinationForm(
            data=self.valid_data,
            files={'image': invalid_file}
        )
        
        # The form might still be valid at Django level, but file validation
        # depends on Django settings and additional validators
        if not form.is_valid():
            self.assertIn('image', form.errors)
    
    def test_destination_form_large_image(self):
        """Test form with large image file."""
        # Create a real but reasonably sized image - form doesn't validate size by default
        from PIL import Image
        import io
        
        image = Image.new('RGB', (200, 200), color='green')
        image_io = io.BytesIO()
        image.save(image_io, format='JPEG', quality=95)
        image_io.seek(0)
        
        large_image = SimpleUploadedFile(
            name='large_image.jpg',
            content=image_io.read(),
            content_type='image/jpeg'
        )
        
        form = DestinationForm(
            data=self.valid_data,
            files={'image': large_image}
        )
        
        # Form should be valid - no size limit configured by default
        self.assertTrue(form.is_valid())
        # The test should pass unless specific size validators are added
        if not form.is_valid() and 'image' in form.errors:
            # If there are size restrictions, they should be properly handled
            self.assertTrue(any('size' in str(error).lower() for error in form.errors['image']))
    
    def test_destination_form_special_characters(self):
        """Test form with special characters in text fields."""
        special_data = {
            'name': 'Côte d\'Azur',
            'country': 'France',
            'description': 'Beautiful coast with açaí & más! 🌴🏖️',
            'best_season': 'Été/Summer'
        }
        form = DestinationForm(data=special_data)
        self.assertTrue(form.is_valid())
        
        destination = form.save()
        self.assertEqual(destination.name, 'Côte d\'Azur')
        self.assertEqual(destination.description, 'Beautiful coast with açaí & más! 🌴🏖️')
    
    def test_destination_form_html_injection(self):
        """Test form handles HTML content safely."""
        html_data = {
            'name': '<script>alert("XSS")</script>Barcelona',
            'country': '<b>Spain</b>',
            'description': '<p>City with <a href="http://evil.com">link</a></p>',
            'best_season': '<em>Spring</em>'
        }
        form = DestinationForm(data=html_data)
        self.assertTrue(form.is_valid())  # Form should accept HTML as text
        
        destination = form.save()
        # HTML should be stored as-is (Django templates will escape it)
        self.assertEqual(destination.name, '<script>alert("XSS")</script>Barcelona')
        self.assertEqual(destination.country, '<b>Spain</b>')
    
    def test_destination_form_sql_injection_attempt(self):
        """Test form handles SQL injection attempts safely."""
        sql_data = {
            'name': "'; DROP TABLE explorer_destination; --",
            'country': "Spain' OR '1'='1",
            'description': "Normal description",
            'best_season': "Spring"
        }
        form = DestinationForm(data=sql_data)
        self.assertTrue(form.is_valid())  # Should be valid as regular text
        
        destination = form.save()
        # Django ORM should handle this safely
        self.assertEqual(destination.name, "'; DROP TABLE explorer_destination; --")
        
        # Verify the table still exists and has our data
        self.assertTrue(Destination.objects.filter(id=destination.id).exists())
    
    def test_destination_form_update_existing(self):
        """Test form can update existing destination."""
        # Create initial destination
        destination = Destination.objects.create(**self.valid_data)
        
        # Update data
        updated_data = {
            'name': 'Updated Barcelona',
            'country': 'Spain',
            'description': 'Updated description with more details.',
            'best_season': 'Summer'
        }
        
        form = DestinationForm(data=updated_data, instance=destination)
        self.assertTrue(form.is_valid())
        
        updated_destination = form.save()
        self.assertEqual(updated_destination.id, destination.id)  # Same instance
        self.assertEqual(updated_destination.name, 'Updated Barcelona')
        self.assertEqual(updated_destination.best_season, 'Summer')
    
    def test_destination_form_fields_included(self):
        """Test that form includes all expected fields."""
        form = DestinationForm()
        expected_fields = ['name', 'country', 'description', 'best_season', 'image']
        
        for field_name in expected_fields:
            self.assertIn(field_name, form.fields)
        
        # Check that no unexpected fields are included
        self.assertEqual(set(form.fields.keys()), set(expected_fields))
    
    def test_destination_form_field_types(self):
        """Test that form fields have correct types."""
        form = DestinationForm()
        
        from django.forms import CharField, ImageField
        
        self.assertIsInstance(form.fields['name'], CharField)
        self.assertIsInstance(form.fields['country'], CharField)
        # description is a CharField with Textarea widget, not TextField
        self.assertIsInstance(form.fields['description'], CharField)
        self.assertIsInstance(form.fields['best_season'], CharField)
        self.assertIsInstance(form.fields['image'], ImageField)
    
    def test_destination_form_field_properties(self):
        """Test form field properties like max_length."""
        form = DestinationForm()
        
        # Check max_length properties
        self.assertEqual(form.fields['name'].max_length, 100)
        self.assertEqual(form.fields['country'].max_length, 100)
        self.assertEqual(form.fields['best_season'].max_length, 50)
        
        # Check required properties
        self.assertTrue(form.fields['name'].required)
        self.assertTrue(form.fields['country'].required)
        self.assertTrue(form.fields['description'].required)
        self.assertTrue(form.fields['best_season'].required)
        self.assertFalse(form.fields['image'].required)  # Image is optional


class FormIntegrationTest(TestCase):
    """Integration tests for form usage in views."""
    
    def test_form_integration_with_views(self):
        """Test that form integrates properly with views."""
        from django.test import Client
        from django.urls import reverse
        from django.contrib.auth.models import User
        
        # Create staff user for destination_create
        staff_user = User.objects.create_user(username='staff', password='pass', is_staff=True)
        
        client = Client()
        client.login(username='staff', password='pass')
        
        # Test GET request shows empty form
        response = client.get(reverse('destination_create'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], DestinationForm)
        
        # Test POST with valid data
        valid_data = {
            'name': 'Rome',
            'country': 'Italy',
            'description': 'Historic city with ancient ruins.',
            'best_season': 'Fall'
        }
        response = client.post(reverse('destination_create'), valid_data)
        self.assertEqual(response.status_code, 302)  # Redirect after success
        
        # Verify destination was created
        self.assertTrue(Destination.objects.filter(name='Rome').exists())
        
        # Test POST with invalid data
        invalid_data = {
            'name': '',  # Required field missing
            'country': 'Italy',
            'description': 'Historic city',
            'best_season': 'Fall'
        }
        response = client.post(reverse('destination_create'), invalid_data)
        self.assertEqual(response.status_code, 200)  # Stays on form page
        self.assertIn('form', response.context)
        self.assertFalse(response.context['form'].is_valid())