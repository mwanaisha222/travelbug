from django.db import models

class Destination(models.Model):
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    description = models.TextField()
    best_season = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Activity(models.Model):
    name = models.CharField(max_length=100)
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='activities')
    description = models.TextField()
    cost_estimate = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

class Traveler(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    favorite_destination = models.ForeignKey(Destination, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name

class Review(models.Model):
    traveler = models.ForeignKey(Traveler, on_delete=models.CASCADE)
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 11)])
    comment = models.TextField()

    def __str__(self):
        return f"{self.traveler.name} - {self.destination.name}"