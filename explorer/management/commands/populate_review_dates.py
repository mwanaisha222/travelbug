from django.core.management.base import BaseCommand
from explorer.models import Review
from datetime import datetime, timedelta
import random


class Command(BaseCommand):
    help = 'Populate created_at dates for existing reviews'

    def handle(self, *args, **kwargs):
        # Update ALL reviews to get a better distribution
        reviews = Review.objects.all()
        count = reviews.count()
        
        if count == 0:
            self.stdout.write(self.style.WARNING('No reviews found!'))
            return
        
        # Generate dates from January 2024 to November 2025
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2025, 11, 10)
        
        updated = 0
        for review in reviews:
            # Generate random date between start and end
            time_between = end_date - start_date
            days_between = time_between.days
            random_days = random.randrange(days_between)
            random_date = start_date + timedelta(days=random_days)
            
            review.created_at = random_date
            review.save()
            updated += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully updated {updated} reviews with random dates distributed throughout 2024-2025!')
        )
