"""
Django management command to populate the database with sample data
for TravelBug application visualization and testing.

Usage: python manage.py populate_data
"""
import random
import os
import urllib.request
import tempfile
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.files import File
from explorer.models import Destination, Activity, Traveler, Review


class Command(BaseCommand):
    help = 'Populates the database with sample data for visualizations'
    
    def download_image(self, url, destination_name):
        """Download image from URL and save it, return the file path"""
        try:
            # Create a temporary file
            img_temp = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
            img_temp.write(urllib.request.urlopen(url).read())
            img_temp.flush()
            img_temp.close()
            return img_temp.name
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Could not download image for {destination_name}: {str(e)}'))
            return None

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting data population...'))
        
        # Clear existing data (optional - comment out if you want to keep existing data)
        self.stdout.write('Clearing existing data...')
        Review.objects.all().delete()
        Activity.objects.all().delete()
        Destination.objects.exclude(name__in=['Santorini', 'Bali']).delete()  # Keep some if they exist
        Traveler.objects.exclude(user__username='admin').delete()
        User.objects.exclude(username='admin').delete()
        
        # Create 25 travelers with users
        self.stdout.write('Creating 25 travelers...')
        travelers = []
        traveler_data = [
            ('John Smith', 'john.smith@email.com'),
            ('Emma Johnson', 'emma.j@email.com'),
            ('Michael Brown', 'michael.b@email.com'),
            ('Sophia Davis', 'sophia.d@email.com'),
            ('William Wilson', 'william.w@email.com'),
            ('Olivia Martinez', 'olivia.m@email.com'),
            ('James Anderson', 'james.a@email.com'),
            ('Ava Taylor', 'ava.t@email.com'),
            ('Robert Thomas', 'robert.t@email.com'),
            ('Isabella Garcia', 'isabella.g@email.com'),
            ('David Rodriguez', 'david.r@email.com'),
            ('Mia Lopez', 'mia.l@email.com'),
            ('Daniel Lee', 'daniel.l@email.com'),
            ('Charlotte White', 'charlotte.w@email.com'),
            ('Matthew Harris', 'matthew.h@email.com'),
            ('Amelia Clark', 'amelia.c@email.com'),
            ('Christopher Lewis', 'chris.l@email.com'),
            ('Harper Walker', 'harper.w@email.com'),
            ('Andrew Hall', 'andrew.h@email.com'),
            ('Evelyn Allen', 'evelyn.a@email.com'),
            ('Joshua Young', 'joshua.y@email.com'),
            ('Abigail King', 'abigail.k@email.com'),
            ('Ryan Wright', 'ryan.w@email.com'),
            ('Emily Scott', 'emily.s@email.com'),
            ('Alexander Green', 'alex.g@email.com'),
        ]
        
        for i, (name, email) in enumerate(traveler_data, 1):
            username = email.split('@')[0].replace('.', '_')
            user = User.objects.create_user(
                username=username,
                email=email,
                password='password123'
            )
            traveler = Traveler.objects.create(
                name=name,
                email=email,
                user=user
            )
            travelers.append(traveler)
        
        self.stdout.write(self.style.SUCCESS(f'Created {len(travelers)} travelers'))
        
        # Create 20+ Uganda destinations with images
        self.stdout.write('Creating 20 Uganda destinations with images...')
        destinations_data = [
            {
                'name': 'Bwindi Impenetrable National Park',
                'country': 'Uganda',
                'description': 'UNESCO World Heritage Site famous for mountain gorilla trekking. Home to almost half of the world\'s remaining mountain gorillas. Ancient rainforest with incredible biodiversity and bird species.',
                'best_season': 'June to September, December to February',
                'image_url': 'https://images.unsplash.com/photo-1534177616072-ef7dc120449d?w=800'
            },
            {
                'name': 'Murchison Falls National Park',
                'country': 'Uganda',
                'description': 'Uganda\'s largest national park featuring the spectacular Murchison Falls where the Nile explodes through a narrow gorge. Abundant wildlife including elephants, lions, giraffes, and hippos.',
                'best_season': 'December to February, June to September',
                'image_url': 'https://images.unsplash.com/photo-1516426122078-c23e76319801?w=800'
            },
            {
                'name': 'Queen Elizabeth National Park',
                'country': 'Uganda',
                'description': 'Famous for tree-climbing lions and diverse ecosystems from savanna to wetlands. Boat safaris on Kazinga Channel offer close encounters with hippos, elephants, and buffalo.',
                'best_season': 'June to September, December to February',
                'image_url': 'https://images.unsplash.com/photo-1547970810-dc1eac37d174?w=800'
            },
            {
                'name': 'Lake Bunyonyi',
                'country': 'Uganda',
                'description': 'One of Africa\'s deepest lakes surrounded by terraced hills. Perfect for swimming, canoeing, and relaxation. 29 islands to explore with stunning scenery and peaceful atmosphere.',
                'best_season': 'Year-round, best June to August, December to February',
                'image_url': 'https://images.unsplash.com/photo-1568602471122-7832951cc4c5?w=800'
            },
            {
                'name': 'Jinja and the Source of the Nile',
                'country': 'Uganda',
                'description': 'Adventure capital of East Africa! White water rafting, bungee jumping, kayaking on the Nile. Historical significance as the source of the world\'s longest river.',
                'best_season': 'Year-round, September to February for rafting',
                'image_url': 'https://images.unsplash.com/photo-1605640840605-14ac1855827b?w=800'
            },
            {
                'name': 'Kampala City',
                'country': 'Uganda',
                'description': 'Uganda\'s vibrant capital city built on seven hills. Cultural sites include Kasubi Tombs (UNESCO site), Uganda Museum, bustling markets, and lively nightlife. Mix of modern and traditional.',
                'best_season': 'Year-round',
                'image_url': 'https://images.unsplash.com/photo-1609137144813-7d9921338f24?w=800'
            },
            {
                'name': 'Rwenzori Mountains',
                'country': 'Uganda',
                'description': 'The legendary "Mountains of the Moon" with Africa\'s third highest peak. Glaciers, unique afro-alpine vegetation, and challenging trekking routes. UNESCO World Heritage Site.',
                'best_season': 'June to August, December to February',
                'image_url': 'https://images.unsplash.com/photo-1589182373726-e4f658ab50b3?w=800'
            },
            {
                'name': 'Kidepo Valley National Park',
                'country': 'Uganda',
                'description': 'Remote wilderness in northeastern Uganda with stunning landscapes. Exceptional game viewing with species not found elsewhere in Uganda including cheetahs and ostriches.',
                'best_season': 'September to March',
                'image_url': 'https://images.unsplash.com/photo-1516426122078-c23e76319801?w=800'
            },
            {
                'name': 'Sipi Falls',
                'country': 'Uganda',
                'description': 'Series of three beautiful waterfalls on the slopes of Mount Elgon. Coffee plantations, rock climbing, and hiking trails. Breathtaking views of the Karamoja plains.',
                'best_season': 'June to August, December to February',
                'image_url': 'https://images.unsplash.com/photo-1523712999610-f77fbcfc3843?w=800'
            },
            {
                'name': 'Lake Mburo National Park',
                'country': 'Uganda',
                'description': 'Compact park perfect for walking safaris and horseback riding. Only park with zebras and impalas. Five lakes attract hippos and variety of water birds.',
                'best_season': 'June to September, December to February',
                'image_url': 'https://images.unsplash.com/photo-1535338622654-26f1ce2ecb20?w=800'
            },
            {
                'name': 'Ssese Islands',
                'country': 'Uganda',
                'description': 'Archipelago of 84 islands on Lake Victoria. Palm-fringed beaches, fishing villages, and tropical paradise atmosphere. Perfect weekend getaway for relaxation.',
                'best_season': 'June to August, December to February',
                'image_url': 'https://images.unsplash.com/photo-1559827260-dc66d52bef19?w=800'
            },
            {
                'name': 'Kibale National Park',
                'country': 'Uganda',
                'description': 'Primate capital of the world! Home to 13 primate species including over 1,500 chimpanzees. Chimpanzee tracking and forest walks through lush tropical rainforest.',
                'best_season': 'December to February, June to September',
                'image_url': 'https://images.unsplash.com/photo-1551497429-deb0d194c5c2?w=800'
            },
            {
                'name': 'Mgahinga Gorilla National Park',
                'country': 'Uganda',
                'description': 'Part of the Virunga Mountains where Uganda, Rwanda, and DR Congo meet. Mountain gorilla trekking and golden monkey tracking. Dramatic volcanic landscapes.',
                'best_season': 'June to September, December to February',
                'image_url': 'https://images.unsplash.com/photo-1534177616072-ef7dc120449d?w=800'
            },
            {
                'name': 'Entebbe',
                'country': 'Uganda',
                'description': 'Charming lakeside town on Lake Victoria shores. Beautiful botanical gardens, wildlife education centre, beaches, and water sports. Gateway to Uganda.',
                'best_season': 'Year-round',
                'image_url': 'https://images.unsplash.com/photo-1552465011-b4e21bf6e79a?w=800'
            },
            {
                'name': 'Fort Portal',
                'country': 'Uganda',
                'description': 'Town surrounded by crater lakes, tea plantations, and stunning scenery. Base for exploring Kibale Forest, Rwenzori Mountains, and Semliki National Park.',
                'best_season': 'Year-round, best December to February',
                'image_url': 'https://images.unsplash.com/photo-1523712999610-f77fbcfc3843?w=800'
            },
            {
                'name': 'Semuliki National Park',
                'country': 'Uganda',
                'description': 'Uganda\'s true tropical lowland forest with Central African wildlife and vegetation. Hot springs, bird watching (over 400 species), and unique biodiversity.',
                'best_season': 'June to September, December to February',
                'image_url': 'https://images.unsplash.com/photo-1551497429-deb0d194c5c2?w=800'
            },
            {
                'name': 'Mount Elgon National Park',
                'country': 'Uganda',
                'description': 'Ancient extinct volcano with the largest volcanic base in the world. Caves, waterfalls, hot springs, and unique montane vegetation. Less crowded trekking experience.',
                'best_season': 'June to August, December to March',
                'image_url': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800'
            },
            {
                'name': 'Ziwa Rhino Sanctuary',
                'country': 'Uganda',
                'description': 'Only place in Uganda to see rhinos in the wild. Conservation success story breeding white rhinos. Walking safaris and rhino tracking on foot.',
                'best_season': 'Year-round',
                'image_url': 'https://images.unsplash.com/photo-1535338622654-26f1ce2ecb20?w=800'
            },
            {
                'name': 'Kasubi Tombs',
                'country': 'Uganda',
                'description': 'UNESCO World Heritage Site and burial ground for Buganda kings. Important cultural and spiritual site with traditional architecture. Learn about Buganda kingdom history.',
                'best_season': 'Year-round',
                'image_url': 'https://images.unsplash.com/photo-1609137144813-7d9921338f24?w=800'
            },
            {
                'name': 'Ngamba Island Chimpanzee Sanctuary',
                'country': 'Uganda',
                'description': 'Sanctuary for orphaned chimps on Lake Victoria. Close encounters with rescued chimpanzees. Educational experience about conservation and wildlife protection.',
                'best_season': 'Year-round',
                'image_url': 'https://images.unsplash.com/photo-1551497429-deb0d194c5c2?w=800'
            },
        ]
        
        destinations = []
        for dest_data in destinations_data:
            image_url = dest_data.pop('image_url', None)
            
            destination, created = Destination.objects.get_or_create(
                name=dest_data['name'],
                defaults=dest_data
            )
            
            # Download and attach image if destination was just created and has image URL
            if created and image_url and not destination.image:
                self.stdout.write(f'  Downloading image for {destination.name}...')
                temp_path = self.download_image(image_url, destination.name)
                if temp_path:
                    with open(temp_path, 'rb') as f:
                        destination.image.save(
                            f'{destination.name.lower().replace(" ", "_")}.jpg',
                            File(f),
                            save=True
                        )
                    # Clean up temporary file
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)
                    
            destinations.append(destination)
        
        self.stdout.write(self.style.SUCCESS(f'Created/verified {len(destinations)} destinations'))
        
        # Assign favorite destinations to travelers
        for traveler in travelers:
            if not traveler.favorite_destination:
                traveler.favorite_destination = random.choice(destinations)
                traveler.save()
        
        # Create Uganda-specific activities (5-8 per destination)
        self.stdout.write('Creating activities...')
        activities_templates = [
            'Gorilla Trekking', 'Chimpanzee Tracking', 'Game Drive', 'Boat Safari',
            'White Water Rafting', 'Bungee Jumping', 'Nature Walk', 'Bird Watching',
            'Mountain Hiking', 'Cultural Village Tour', 'Photography Safari', 'Fishing',
            'Horseback Riding', 'Canoeing', 'Swimming', 'Camping',
            'Wildlife Viewing', 'Waterfall Hiking', 'Community Tours', 'Coffee Plantation Tour',
            'Tea Estate Visit', 'Hot Springs Visit', 'Cave Exploration', 'Rock Climbing',
            'Golden Monkey Tracking', 'Rhino Tracking', 'Night Game Drive', 'Bush Walk',
            'Kayaking', 'Island Hopping', 'Sunset Cruise', 'Traditional Dance Show'
        ]
        
        total_activities = 0
        for destination in destinations:
            num_activities = random.randint(5, 8)
            selected_activities = random.sample(activities_templates, num_activities)
            
            for activity_name in selected_activities:
                description = f'Experience {activity_name.lower()} in {destination.name}. A must-do activity for visitors!'
                cost = round(random.uniform(20.00, 500.00), 2)  # Random cost between $20 and $500
                
                Activity.objects.create(
                    destination=destination,
                    name=activity_name,
                    description=description,
                    cost_estimate=cost
                )
                total_activities += 1
        
        self.stdout.write(self.style.SUCCESS(f'Created {total_activities} activities'))
        
        # Create reviews (multiple reviews per destination from different travelers)
        self.stdout.write('Creating reviews...')
        review_comments = [
            "Absolutely stunning! Exceeded all my expectations. Would definitely visit again.",
            "Beautiful place with amazing scenery. The local culture is fascinating.",
            "One of the best trips I've ever taken. Highly recommend to everyone.",
            "Great experience overall, though a bit crowded during peak season.",
            "Worth every penny! The views alone make this destination special.",
            "Amazing destination! The food was incredible and people were so friendly.",
            "Breathtaking beauty everywhere you look. Perfect for photography enthusiasts.",
            "Had an incredible time! So many activities to choose from.",
            "This place is magical! Definitely living up to its reputation.",
            "Good destination but quite expensive. Budget accordingly.",
            "Perfect getaway! Relaxing, beautiful, and culturally rich.",
            "Exceeded expectations! Every moment was picture-perfect.",
            "Nice place to visit but I expected more. Still enjoyable though.",
            "Absolutely loved it! The perfect blend of adventure and relaxation.",
            "Outstanding destination! Would return in a heartbeat.",
            "Beautiful scenery and rich history. Educational and enjoyable.",
            "Great for couples and families alike. Something for everyone.",
            "Wonderful experience! The local guides were knowledgeable and friendly.",
            "Paradise on earth! Can't wait to come back.",
            "Good destination overall. A few tourist traps but mostly authentic.",
            "Incredible experience from start to finish. Highly recommended!",
            "Beautiful place but quite touristy. Go in off-season if possible.",
            "Amazing! The hospitality and warmth of locals made it extra special.",
            "Stunning destination! Worth the long journey to get there.",
            "Perfect vacation spot! Great weather, food, and activities.",
            "Lovely place with so much to see and do. Need at least a week here.",
            "Fantastic destination! Already planning my return trip.",
            "Very impressive! The natural beauty is unmatched.",
            "Great place to unwind and explore. Loved every minute.",
            "Wonderful destination with rich culture and friendly people.",
        ]
        
        total_reviews = 0
        for destination in destinations:
            # Each destination gets 8-15 reviews from different travelers
            num_reviews = random.randint(8, 15)
            reviewing_travelers = random.sample(travelers, num_reviews)
            
            for traveler in reviewing_travelers:
                rating = random.choices(
                    range(1, 11),
                    weights=[1, 1, 2, 3, 5, 8, 12, 15, 20, 25],  # Bias toward higher ratings
                    k=1
                )[0]
                
                comment = random.choice(review_comments)
                
                Review.objects.create(
                    destination=destination,
                    traveler=traveler,
                    rating=rating,
                    comment=comment
                )
                total_reviews += 1
        
        self.stdout.write(self.style.SUCCESS(f'Created {total_reviews} reviews'))
        
        # Print summary
        self.stdout.write(self.style.SUCCESS('\n' + '='*50))
        self.stdout.write(self.style.SUCCESS('DATA POPULATION COMPLETE!'))
        self.stdout.write(self.style.SUCCESS('='*50))
        self.stdout.write(f'✓ Travelers: {Traveler.objects.count()}')
        self.stdout.write(f'✓ Destinations: {Destination.objects.count()}')
        self.stdout.write(f'✓ Activities: {Activity.objects.count()}')
        self.stdout.write(f'✓ Reviews: {Review.objects.count()}')
        self.stdout.write(self.style.SUCCESS('='*50))
        self.stdout.write(self.style.SUCCESS('\nYou can now proceed with data visualizations!'))
