"""
Analytics module for TravelBug application.
Generates various data visualizations for the analytics dashboard.
"""
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from django.db.models import Count, Avg
from .models import Destination, Activity, Review, Traveler


def get_analytics_summary():
    """
    Get summary statistics for the analytics dashboard.
    Returns a dictionary with key metrics.
    """
    summary = {
        'total_destinations': Destination.objects.count(),
        'total_reviews': Review.objects.count(),
        'total_activities': Activity.objects.count(),
        'total_travelers': Traveler.objects.count(),
        'avg_rating': Review.objects.aggregate(Avg('rating'))['rating__avg'] or 0,
    }
    return summary


def generate_destination_popularity_bar():
    """
    Generate a bar chart showing destination popularity by number of reviews.
    Uses gradient purple colors with professional styling.
    """
    # Get destination review counts
    destinations = Destination.objects.annotate(
        review_count=Count('reviews')
    ).order_by('-review_count')[:10]
    
    if not destinations:
        return "<p>No data available</p>"
    
    names = [d.name for d in destinations]
    counts = [d.review_count for d in destinations]
    
    # Create bar chart with gradient colors
    fig = go.Figure(data=[
        go.Bar(
            x=names,
            y=counts,
            marker=dict(
                color=counts,
                colorscale=[[0, 'rgba(102, 126, 234, 0.6)'], [1, 'rgba(102, 126, 234, 1)']],
                line=dict(color='rgba(102, 126, 234, 1)', width=2)
            ),
            text=counts,
            textposition='outside',
            textfont=dict(size=14, family='Arial Black', color='#333'),
            hovertemplate='<b>%{x}</b><br>' +
                          '📊 Reviews: %{y}<br>' +
                          '<extra></extra>',
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Arial",
                bordercolor='rgba(102, 126, 234, 1)'
            )
        )
    ])
    
    fig.update_layout(
        title={
            'text': 'Top 10 Destinations by Popularity',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'family': 'Arial Black', 'color': '#333'}
        },
        xaxis_title='Destination',
        yaxis_title='Number of Reviews',
        font=dict(family='Arial', size=12, color='#333'),
        plot_bgcolor='rgba(245, 247, 250, 0.5)',
        paper_bgcolor='white',
        margin=dict(l=80, r=40, t=120, b=120),
        height=450,
        yaxis=dict(range=[0, 18]),
        xaxis=dict(tickangle=-45, tickfont=dict(size=11))
    )
    
    return fig.to_html(full_html=False)


def generate_destination_ratings_bar():
    """
    Generate a bar chart showing average ratings for destinations.
    Uses color coding: green (≥8), orange (6-8), red (<6).
    """
    # Get destinations with average ratings
    destinations = Destination.objects.annotate(
        avg_rating=Avg('reviews__rating')
    ).filter(avg_rating__isnull=False).order_by('-avg_rating')[:10]
    
    if not destinations:
        return "<p>No data available</p>"
    
    names = [d.name for d in destinations]
    ratings = [float(d.avg_rating) for d in destinations]
    
    # Color code bars based on rating
    colors = []
    for rating in ratings:
        if rating >= 8:
            colors.append('rgba(16, 185, 129, 0.8)')  # Green
        elif rating >= 6:
            colors.append('rgba(245, 158, 11, 0.8)')  # Orange
        else:
            colors.append('rgba(239, 68, 68, 0.8)')   # Red
    
    fig = go.Figure(data=[
        go.Bar(
            x=names,
            y=ratings,
            marker=dict(
                color=colors,
                line=dict(color='rgba(0, 0, 0, 0.2)', width=2)
            ),
            text=[f'{r:.1f}' for r in ratings],
            textposition='outside',
            textfont=dict(size=14, family='Arial Black', color='#333'),
            hovertemplate='<b>%{x}</b><br>' +
                          '⭐ Rating: %{y:.1f}/10<br>' +
                          '<extra></extra>',
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Arial"
            )
        )
    ])
    
    # Add reference lines
    fig.add_hline(y=8.0, line_dash="dash", line_color="rgba(16, 185, 129, 0.5)",
                  annotation_text="Excellent (8.0)", annotation_position="right")
    fig.add_hline(y=6.0, line_dash="dash", line_color="rgba(245, 158, 11, 0.5)",
                  annotation_text="Good (6.0)", annotation_position="right")
    
    fig.update_layout(
        title={
            'text': 'Top 10 Destinations by Average Rating',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'family': 'Arial Black', 'color': '#333'}
        },
        xaxis_title='Destination',
        yaxis_title='Average Rating',
        font=dict(family='Arial', size=12, color='#333'),
        plot_bgcolor='rgba(245, 247, 250, 0.5)',
        paper_bgcolor='white',
        margin=dict(l=80, r=40, t=120, b=120),
        height=450,
        yaxis=dict(range=[0, 11]),
        xaxis=dict(tickangle=-45, tickfont=dict(size=11))
    )
    
    return fig.to_html(full_html=False)


def generate_activity_distribution_pie():
    """
    Generate a donut chart showing activity distribution by destination.
    """
    # Get activity counts by destination
    activities = Activity.objects.values('destination__name').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    if not activities:
        return "<p>No data available</p>"
    
    labels = [a['destination__name'] for a in activities]
    values = [a['count'] for a in activities]
    
    fig = go.Figure(data=[
        go.Pie(
            labels=labels,
            values=values,
            hole=0.3,
            marker=dict(colors=px.colors.qualitative.Set3),
            textinfo='label+percent',
            textfont=dict(size=13, family='Arial'),
            hovertemplate='<b>%{label}</b><br>' +
                          'Activities: %{value}<br>' +
                          'Percentage: %{percent}<br>' +
                          '<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title={
            'text': 'Activity Distribution by Destination',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'family': 'Arial Black', 'color': '#333'}
        },
        font=dict(family='Arial', size=12, color='#333'),
        paper_bgcolor='white',
        height=550,
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.02
        )
    )
    
    return fig.to_html(full_html=False)


def generate_traveler_preferences_pie():
    """
    Generate a pie chart showing traveler preferences by favorite destination.
    """
    # Get traveler counts by favorite destination
    travelers = Traveler.objects.filter(
        favorite_destination__isnull=False
    ).values('favorite_destination__name').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    if not travelers:
        return "<p>No data available</p>"
    
    labels = [t['favorite_destination__name'] for t in travelers]
    values = [t['count'] for t in travelers]
    
    fig = go.Figure(data=[
        go.Pie(
            labels=labels,
            values=values,
            marker=dict(colors=px.colors.sequential.Purples_r),
            textinfo='label+percent',
            textfont=dict(size=13, family='Arial'),
            hovertemplate='<b>%{label}</b><br>' +
                          'Travelers: %{value}<br>' +
                          'Percentage: %{percent}<br>' +
                          '<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title={
            'text': 'Traveler Favorite Destinations',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'family': 'Arial Black', 'color': '#333'}
        },
        font=dict(family='Arial', size=12, color='#333'),
        paper_bgcolor='white',
        height=550,
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.02
        )
    )
    
    return fig.to_html(full_html=False)


def generate_rating_trends_line():
    """
    Generate a line chart showing rating trends.
    Shows individual reviews as scatter points and cumulative average as a line.
    """
    # Get all reviews ordered by ID (as a proxy for creation order)
    reviews = Review.objects.select_related('destination').order_by('id')
    
    if not reviews:
        return "<p>No data available</p>"
    
    # Use review IDs as x-axis since there's no timestamp
    review_ids = list(range(1, len(reviews) + 1))
    ratings = [r.rating for r in reviews]
    destinations = [r.destination.name for r in reviews]
    
    # Calculate cumulative average
    cumulative_avg = []
    for i in range(len(ratings)):
        avg = sum(ratings[:i+1]) / (i+1)
        cumulative_avg.append(avg)
    
    fig = go.Figure()
    
    # Add scatter points for individual reviews
    fig.add_trace(go.Scatter(
        x=review_ids,
        y=ratings,
        mode='markers',
        name='Individual Reviews',
        marker=dict(size=8, color='rgba(102, 126, 234, 0.6)', line=dict(width=1, color='white')),
        text=destinations,
        hovertemplate='<b>%{text}</b><br>' +
                      'Review #: %{x}<br>' +
                      'Rating: %{y}/10<br>' +
                      '<extra></extra>'
    ))
    
    # Add cumulative average line
    fig.add_trace(go.Scatter(
        x=review_ids,
        y=cumulative_avg,
        mode='lines',
        name='Cumulative Average',
        line=dict(color='rgba(16, 185, 129, 1)', width=3),
        hovertemplate='Average: %{y:.2f}/10<br>' +
                      '<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': 'Rating Trends',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'family': 'Arial Black', 'color': '#333'}
        },
        xaxis_title='Review Number',
        yaxis_title='Rating',
        font=dict(family='Arial', size=12, color='#333'),
        plot_bgcolor='rgba(245, 247, 250, 0.5)',
        paper_bgcolor='white',
        height=500,
        yaxis=dict(range=[0, 10]),
        hovermode='closest',
        showlegend=True
    )
    
    return fig.to_html(full_html=False)


def generate_seasonal_heatmap():
    """
    Generate a heatmap showing number of visitors (reviews) per destination by month.
    """
    from collections import defaultdict
    
    # Get all reviews with dates
    reviews = Review.objects.select_related('destination').filter(created_at__isnull=False)
    
    if not reviews:
        return "<p>No review data available</p>"
    
    # Count reviews by destination and month
    month_counts = defaultdict(lambda: [0] * 12)  # destination_name -> [count for each month]
    destination_set = set()
    
    for review in reviews:
        dest_name = review.destination.name
        month_index = review.created_at.month - 1  # Convert 1-12 to 0-11
        month_counts[dest_name][month_index] += 1
        destination_set.add(dest_name)
    
    # Get top destinations by total reviews
    dest_totals = [(dest, sum(counts)) for dest, counts in month_counts.items()]
    dest_totals.sort(key=lambda x: x[1], reverse=True)
    top_destinations = [dest for dest, _ in dest_totals[:15]]  # Top 15
    
    if not top_destinations:
        return "<p>No visitor data available</p>"
    
    # Prepare data for heatmap
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    heatmap_data = []
    dest_names = []
    
    for dest in top_destinations:
        dest_names.append(dest)
        heatmap_data.append(month_counts[dest])
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data,
        x=months,
        y=dest_names,
        colorscale='Blues',
        showscale=True,
        colorbar=dict(title="Visitors"),
        hovertemplate='<b>%{y}</b><br>' +
                      'Month: %{x}<br>' +
                      'Visitors: %{z}<br>' +
                      '<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': 'Visitor Distribution by Month',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'family': 'Arial Black', 'color': '#333'}
        },
        xaxis_title='Month',
        yaxis_title='Destination',
        font=dict(family='Arial', size=12, color='#333'),
        paper_bgcolor='white',
        height=600,
        yaxis=dict(tickfont=dict(size=10))
    )
    
    return fig.to_html(full_html=False)


def generate_rating_distribution():
    """
    Generate a histogram showing the distribution of ratings.
    """
    # Get all ratings
    reviews = Review.objects.all()
    
    if not reviews:
        return "<p>No data available</p>"
    
    ratings = [r.rating for r in reviews]
    
    fig = go.Figure(data=[
        go.Histogram(
            x=ratings,
            nbinsx=10,
            marker=dict(
                color='rgba(102, 126, 234, 0.7)',
                line=dict(color='rgba(102, 126, 234, 1)', width=2)
            ),
            hovertemplate='Rating: %{x}<br>' +
                          'Count: %{y}<br>' +
                          '<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title={
            'text': 'Rating Distribution',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'family': 'Arial Black', 'color': '#333'}
        },
        xaxis_title='Rating',
        yaxis_title='Frequency',
        font=dict(family='Arial', size=12, color='#333'),
        plot_bgcolor='rgba(245, 247, 250, 0.5)',
        paper_bgcolor='white',
        height=500,
        xaxis=dict(range=[0, 11], dtick=1),
        bargap=0.1
    )
    
    return fig.to_html(full_html=False)


def generate_top_destinations_comparison():
    """
    Generate a multi-metric comparison chart for top destinations.
    Shows review count, average rating, and activity count side by side.
    """
    # Get top 8 destinations by review count
    destinations = Destination.objects.annotate(
        review_count=Count('reviews'),
        avg_rating=Avg('reviews__rating'),
        activity_count=Count('activities')
    ).order_by('-review_count')[:8]
    
    if not destinations:
        return "<p>No data available</p>"
    
    names = [d.name for d in destinations]
    reviews = [d.review_count for d in destinations]
    ratings = [float(d.avg_rating) if d.avg_rating else 0 for d in destinations]
    activities = [d.activity_count for d in destinations]
    
    # Create subplots
    fig = make_subplots(
        rows=1, cols=3,
        subplot_titles=('Reviews', 'Average Rating', 'Activities'),
        horizontal_spacing=0.12
    )
    
    # Reviews subplot
    fig.add_trace(
        go.Bar(
            x=names,
            y=reviews,
            name='Reviews',
            marker=dict(color='rgba(102, 126, 234, 0.8)'),
            text=reviews,
            textposition='outside',
            textfont=dict(size=11, family='Arial Black'),
            showlegend=False,
            hovertemplate='<b>%{x}</b><br>Reviews: %{y}<extra></extra>'
        ),
        row=1, col=1
    )
    
    # Ratings subplot
    fig.add_trace(
        go.Bar(
            x=names,
            y=ratings,
            name='Rating',
            marker=dict(color='rgba(16, 185, 129, 0.8)'),
            text=[f'{r:.1f}' for r in ratings],
            textposition='outside',
            textfont=dict(size=11, family='Arial Black'),
            showlegend=False,
            hovertemplate='<b>%{x}</b><br>Rating: %{y:.1f}<extra></extra>'
        ),
        row=1, col=2
    )
    
    # Activities subplot
    fig.add_trace(
        go.Bar(
            x=names,
            y=activities,
            name='Activities',
            marker=dict(color='rgba(245, 158, 11, 0.8)'),
            text=activities,
            textposition='outside',
            textfont=dict(size=11, family='Arial Black'),
            showlegend=False,
            hovertemplate='<b>%{x}</b><br>Activities: %{y}<extra></extra>'
        ),
        row=1, col=3
    )
    
    # Update layout
    fig.update_layout(
        title={
            'text': 'Top Destinations Multi-Metric Comparison',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'family': 'Arial Black', 'color': '#333'}
        },
        font=dict(family='Arial', size=11, color='#333'),
        plot_bgcolor='rgba(245, 247, 250, 0.5)',
        paper_bgcolor='white',
        height=550,
        margin=dict(l=60, r=40, t=100, b=150)
    )
    
    # Update all x-axes
    fig.update_xaxes(tickangle=-45, tickfont=dict(size=9))
    
    # Update y-axes
    fig.update_yaxes(title_text="Count", row=1, col=1)
    fig.update_yaxes(title_text="Rating (0-10)", row=1, col=2, range=[0, 10])
    fig.update_yaxes(title_text="Count", row=1, col=3)
    
    return fig.to_html(full_html=False)
