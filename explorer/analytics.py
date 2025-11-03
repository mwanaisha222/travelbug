"""
Analytics module for TravelBug - generates data visualizations
"""
import io
import base64
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from django.db.models import Avg, Count, Q
from .models import Destination, Activity, Traveler, Review


# Set style for matplotlib/seaborn
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 10


def get_base64_image(plt):
    """Convert matplotlib plot to base64 encoded image"""
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    graphic = base64.b64encode(image_png)
    return graphic.decode('utf-8')


def generate_destination_popularity_bar():
    """Bar graph showing destination popularity by review count"""
    destinations = Destination.objects.annotate(
        review_count=Count('reviews'),
        avg_rating=Avg('reviews__rating')
    ).order_by('-review_count')[:10]
    
    df = pd.DataFrame(list(destinations.values('name', 'review_count', 'avg_rating')))
    
    if df.empty:
        return None
    
    # Create plotly bar chart
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df['name'],
        y=df['review_count'],
        marker_color='#667eea',
        text=df['review_count'],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Reviews: %{y}<br>Avg Rating: %{customdata:.1f}/10<extra></extra>',
        customdata=df['avg_rating']
    ))
    
    fig.update_layout(
        title='Top 10 Most Popular Destinations by Review Count',
        xaxis_title='Destination',
        yaxis_title='Number of Reviews',
        template='plotly_white',
        height=500,
        font=dict(size=12),
        title_font_size=16,
        xaxis_tickangle=-45
    )
    
    return fig.to_html(full_html=False, include_plotlyjs='cdn')


def generate_destination_ratings_bar():
    """Bar graph showing destinations by average rating"""
    destinations = Destination.objects.annotate(
        avg_rating=Avg('reviews__rating'),
        review_count=Count('reviews')
    ).filter(review_count__gte=3).order_by('-avg_rating')[:10]
    
    df = pd.DataFrame(list(destinations.values('name', 'avg_rating', 'review_count')))
    
    if df.empty:
        return None
    
    fig = go.Figure()
    
    # Color gradient based on rating
    colors = ['#10b981' if x >= 8 else '#f59e0b' if x >= 6 else '#ef4444' 
              for x in df['avg_rating']]
    
    fig.add_trace(go.Bar(
        x=df['name'],
        y=df['avg_rating'],
        marker_color=colors,
        text=[f'{x:.1f}' for x in df['avg_rating']],
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Avg Rating: %{y:.1f}/10<br>Reviews: %{customdata}<extra></extra>',
        customdata=df['review_count']
    ))
    
    fig.update_layout(
        title='Top 10 Highest Rated Destinations',
        xaxis_title='Destination',
        yaxis_title='Average Rating (out of 10)',
        template='plotly_white',
        height=500,
        font=dict(size=12),
        title_font_size=16,
        xaxis_tickangle=-45,
        yaxis=dict(range=[0, 10])
    )
    
    return fig.to_html(full_html=False, include_plotlyjs='cdn')


def generate_activity_distribution_pie():
    """Pie chart showing activity type distribution"""
    activities = Activity.objects.values('name').annotate(
        count=Count('id')
    ).order_by('-count')
    
    df = pd.DataFrame(list(activities))
    
    if df.empty:
        return None
    
    # Group smaller activities into "Other"
    if len(df) > 10:
        top_9 = df.head(9)
        others_sum = df.tail(len(df) - 9)['count'].sum()
        other_row = pd.DataFrame([{'name': 'Other Activities', 'count': others_sum}])
        df = pd.concat([top_9, other_row], ignore_index=True)
    
    fig = go.Figure(data=[go.Pie(
        labels=df['name'],
        values=df['count'],
        hole=.3,
        marker=dict(colors=px.colors.qualitative.Set3),
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        title='Activity Type Distribution Across Destinations',
        template='plotly_white',
        height=550,
        width=None,
        font=dict(size=12),
        title_font_size=16,
        margin=dict(l=20, r=20, t=80, b=20)
    )
    
    return fig.to_html(full_html=False, include_plotlyjs='cdn')


def generate_traveler_preferences_pie():
    """Pie chart showing traveler favorite destination preferences"""
    favorites = Traveler.objects.filter(
        favorite_destination__isnull=False
    ).values('favorite_destination__name').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    df = pd.DataFrame(list(favorites))
    
    if df.empty:
        return None
    
    df.columns = ['destination', 'count']
    
    fig = go.Figure(data=[go.Pie(
        labels=df['destination'],
        values=df['count'],
        marker=dict(colors=px.colors.sequential.Purples_r),
        textinfo='label+value',
        hovertemplate='<b>%{label}</b><br>Travelers: %{value}<br>Percentage: %{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        title='Top Traveler Favorite Destinations',
        template='plotly_white',
        height=550,
        width=None,
        font=dict(size=12),
        title_font_size=16,
        margin=dict(l=20, r=20, t=80, b=20)
    )
    
    return fig.to_html(full_html=False, include_plotlyjs='cdn')


def generate_rating_trends_line():
    """Line graph showing rating trends over time"""
    reviews = Review.objects.all().order_by('id')
    
    if not reviews.exists():
        return None
    
    # Create cumulative average rating
    ratings_data = []
    cumulative_sum = 0
    
    for idx, review in enumerate(reviews, 1):
        cumulative_sum += review.rating
        avg_rating = cumulative_sum / idx
        ratings_data.append({
            'review_number': idx,
            'rating': review.rating,
            'cumulative_avg': avg_rating,
            'destination': review.destination.name
        })
    
    df = pd.DataFrame(ratings_data)
    
    fig = go.Figure()
    
    # Add individual ratings as scatter
    fig.add_trace(go.Scatter(
        x=df['review_number'],
        y=df['rating'],
        mode='markers',
        name='Individual Ratings',
        marker=dict(size=6, color='#cbd5e0', opacity=0.6),
        hovertemplate='Review #%{x}<br>Rating: %{y}/10<br>%{text}<extra></extra>',
        text=df['destination']
    ))
    
    # Add cumulative average as line
    fig.add_trace(go.Scatter(
        x=df['review_number'],
        y=df['cumulative_avg'],
        mode='lines',
        name='Cumulative Average',
        line=dict(color='#667eea', width=3),
        hovertemplate='Review #%{x}<br>Avg Rating: %{y:.2f}/10<extra></extra>'
    ))
    
    fig.update_layout(
        title='Rating Trends - Individual Reviews vs. Cumulative Average',
        xaxis_title='Review Number',
        yaxis_title='Rating (out of 10)',
        template='plotly_white',
        height=500,
        font=dict(size=12),
        title_font_size=16,
        hovermode='x unified',
        yaxis=dict(range=[0, 10])
    )
    
    return fig.to_html(full_html=False, include_plotlyjs='cdn')


def generate_seasonal_heatmap():
    """Heat map showing seasonal tourism based on best_season data"""
    destinations = Destination.objects.all()
    
    if not destinations.exists():
        return None
    
    # Parse seasons from best_season field
    season_data = {
        'January': 0, 'February': 0, 'March': 0, 'April': 0,
        'May': 0, 'June': 0, 'July': 0, 'August': 0,
        'September': 0, 'October': 0, 'November': 0, 'December': 0
    }
    
    month_mapping = {
        'jan': 'January', 'feb': 'February', 'mar': 'March', 'apr': 'April',
        'may': 'May', 'jun': 'June', 'jul': 'July', 'aug': 'August',
        'sep': 'September', 'oct': 'October', 'nov': 'November', 'dec': 'December'
    }
    
    for dest in destinations:
        season_text = dest.best_season.lower()
        
        # Check for year-round
        if 'year' in season_text or 'all' in season_text:
            for month in season_data.keys():
                season_data[month] += 1
        else:
            # Check for specific months
            for abbr, full_name in month_mapping.items():
                if abbr in season_text or full_name.lower() in season_text:
                    season_data[full_name] += 1
    
    months = list(season_data.keys())
    values = list(season_data.values())
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=[values],
        x=months,
        y=['Destinations'],
        colorscale='Purples',
        text=[[str(v) for v in values]],
        texttemplate='%{text}',
        textfont={"size": 14},
        hovertemplate='<b>%{x}</b><br>Destinations: %{z}<extra></extra>',
        colorbar=dict(title="Number of<br>Destinations")
    ))
    
    fig.update_layout(
        title='Seasonal Tourism - Best Months to Visit Uganda Destinations',
        xaxis_title='Month',
        template='plotly_white',
        height=300,
        font=dict(size=12),
        title_font_size=16
    )
    
    return fig.to_html(full_html=False, include_plotlyjs='cdn')


def generate_rating_distribution():
    """Distribution of all ratings"""
    reviews = Review.objects.all()
    
    if not reviews.exists():
        return None
    
    df = pd.DataFrame(list(reviews.values('rating')))
    
    fig = go.Figure()
    
    fig.add_trace(go.Histogram(
        x=df['rating'],
        nbinsx=10,
        marker_color='#667eea',
        hovertemplate='Rating: %{x}<br>Count: %{y}<extra></extra>'
    ))
    
    fig.update_layout(
        title='Rating Distribution - All Reviews',
        xaxis_title='Rating (1-10)',
        yaxis_title='Number of Reviews',
        template='plotly_white',
        height=400,
        font=dict(size=12),
        title_font_size=16,
        xaxis=dict(tickmode='linear', tick0=1, dtick=1)
    )
    
    return fig.to_html(full_html=False, include_plotlyjs='cdn')


def generate_top_destinations_comparison():
    """Multi-metric comparison of top destinations"""
    destinations = Destination.objects.annotate(
        review_count=Count('reviews'),
        avg_rating=Avg('reviews__rating'),
        activity_count=Count('activities')
    ).order_by('-review_count')[:8]
    
    df = pd.DataFrame(list(destinations.values(
        'name', 'review_count', 'avg_rating', 'activity_count'
    )))
    
    if df.empty:
        return None
    
    # Create subplots
    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=('Reviews', 'Average Rating', 'Activities'),
        specs=[[{'type': 'bar'}, {'type': 'bar'}, {'type': 'bar'}]]
    )
    
    # Reviews
    fig.add_trace(
        go.Bar(x=df['name'], y=df['review_count'], marker_color='#667eea',
               name='Reviews', showlegend=False),
        row=1, col=1
    )
    
    # Average Rating
    fig.add_trace(
        go.Bar(x=df['name'], y=df['avg_rating'], marker_color='#10b981',
               name='Avg Rating', showlegend=False),
        row=1, col=2
    )
    
    # Activities
    fig.add_trace(
        go.Bar(x=df['name'], y=df['activity_count'], marker_color='#f59e0b',
               name='Activities', showlegend=False),
        row=1, col=3
    )
    
    fig.update_xaxes(tickangle=-45)
    fig.update_layout(
        title_text='Top Destinations - Multi-Metric Comparison',
        height=500,
        template='plotly_white',
        font=dict(size=10),
        title_font_size=16
    )
    
    return fig.to_html(full_html=False, include_plotlyjs='cdn')


def get_analytics_summary():
    """Get summary statistics for dashboard"""
    total_destinations = Destination.objects.count()
    total_reviews = Review.objects.count()
    total_travelers = Traveler.objects.count()
    total_activities = Activity.objects.count()
    
    avg_rating = Review.objects.aggregate(avg=Avg('rating'))['avg'] or 0
    
    top_destination = Destination.objects.annotate(
        review_count=Count('reviews')
    ).order_by('-review_count').first()
    
    return {
        'total_destinations': total_destinations,
        'total_reviews': total_reviews,
        'total_travelers': total_travelers,
        'total_activities': total_activities,
        'average_rating': round(avg_rating, 2),
        'top_destination': top_destination.name if top_destination else 'N/A',
    }
