TravelBucket
The travel bucket app is a simple web application that allows users to explore different travel destinations, discover fun activities at each location, view traveler profiles and their favorite destinations, and read reviews with ratings and comments from other travelers. Through these four sections—destinations, activities, travelers, and reviews—the app provides an engaging way for users to browse travel experiences while demonstrating the use of models, views, templates, and URLs in Django.

It is a Django web application designed to demonstrate the Model-View-Controller (MVC) pattern. It includes one app, explorer, which manages travel-related data such as destinations, activities, travelers, and reviews. The app features four models, four views, four templates, and corresponding URLs, styled with Bootstrap for a clean and responsive user interface.
Features

Destination List Page: Displays a list of travel destinations with their name, country, description, and best season to visit.
Activities Page: Shows activities available for a specific destination, including descriptions and cost estimates.
Traveler Profile Page: Displays a traveler's name, email, and favorite destination.
Reviews Page: Lists reviews for a destination, including ratings and comments from travelers.
Admin Interface: Allows administrators to manage destinations, activities, travelers, and reviews.
Responsive Design: Uses Bootstrap 5.3 for visually appealing cards, lists, and navigation.

Project Structure
TravelBucket/
├── explorer/
│   ├── migrations/
│   ├── templates/
│   │   ├── explorer/
│   │   │   ├── base.html
│   │   │   ├── destination_list.html
│   │   │   ├── activities.html
│   │   │   ├── traveler_profile.html
│   │   │   ├── reviews.html
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── urls.py
│   ├── views.py
├── TravelBucket/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
├── db.sqlite3
├── manage.py
├── README.md

Requirements

Python 3.8+
Django 5.1+
Bootstrap 5.3 (included via CDN)
SQLite (default database, included with Django)

Setup Instructions

Clone the Repository (if hosted on a version control system):
git clone <repository-url>
cd TravelBucket


Create a Virtual Environment:
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


Install Dependencies:
pip install django


Apply Migrations:Navigate to the project directory (TravelBucket/) and run:
python manage.py makemigrations
python manage.py migrate


Create a Superuser (for admin access):
python manage.py createsuperuser


Run the Development Server:
python manage.py runserver


Access the Application:

Open a browser and visit http://127.0.0.1:8000/ to see the destination list.
Access the admin interface at http://127.0.0.1:8000/admin/ to add data.



URLs

Home (Destination List): http://127.0.0.1:8000/
Activities for a Destination: http://127.0.0.1:8000/destinations/<destination_id>/activities/
Traveler Profile: http://127.0.0.1:8000/travelers/<traveler_id>/
Reviews for a Destination: http://127.0.0.1:8000/destinations/<destination_id>/reviews/
Admin Interface: http://127.0.0.1:8000/admin/

Models

Destination:
Fields: name (CharField), country (CharField), description (TextField), best_season (CharField)


Activity:
Fields: name (CharField), destination (ForeignKey to Destination), description (TextField), cost_estimate (DecimalField)


Traveler:
Fields: name (CharField), email (EmailField), favorite_destination (ForeignKey to Destination, nullable)


Review:
Fields: traveler (ForeignKey to Traveler), destination (ForeignKey to Destination), rating (IntegerField, 1-10), comment (TextField)



Views and Templates

destination_list: Renders destination_list.html, showing all destinations in cards.
activities_page: Renders activities.html, listing activities for a specific destination.
traveler_profile: Renders traveler_profile.html, showing a traveler’s details.
reviews_page: Renders reviews.html, listing reviews for a specific destination.

Adding Data

Log in to the admin interface at http://127.0.0.1:8000/admin/.
Add instances of Destination, Activity, Traveler, and Review to populate the database.
Example:
Create a Destination (e.g., Name: "Paris", Country: "France", Description: "City of Light", Best Season: "Spring").
Add an Activity linked to a destination (e.g., Name: "Eiffel Tower Tour", Cost Estimate: 50.00).
Add a Traveler with a favorite destination.
Add a Review linking a traveler and destination.



Notes

Templates are stored in explorer/templates/explorer/ to follow Django’s app-specific template organization.
The app uses Bootstrap 5.3 via CDN for styling, ensuring responsiveness and a modern look.
Traveler profile URLs require a traveler_id. In a production app, you might add a traveler list view for easier navigation.
If you encounter a TemplateDoesNotExist error, ensure templates are in explorer/templates/explorer/.
To customize the database, replace SQLite with another backend (e.g., PostgreSQL) in settings.py.

Troubleshooting

404 Error on Root URL: Ensure explorer/urls.py maps '' to the destination_list view.
TemplateDoesNotExist: Verify templates are in explorer/templates/explorer/.
No Data Displayed: Add data via the admin interface.
Static Files: This project uses Bootstrap via CDN, so no local static files are required.


