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
    Uses multiple vibrant colors.
    """
    # Get destination review counts
    destinations = Destination.objects.annotate(
        review_count=Count('reviews')
    ).order_by('-review_count')[:10]
    
    if not destinations:
        return "<p>No data available</p>"
    
    names = [d.name for d in destinations]
    counts = [d.review_count for d in destinations]
    
    # Create colorful bar chart with multiple colors
    colors = [
        '#3b82f6',  # Blue
        '#8b5cf6',  # Purple
        '#f97316',  # Orange
        '#10b981',  # Green
        '#06b6d4',  # Cyan
        '#ec4899',  # Pink
        '#f59e0b',  # Amber
        '#6366f1',  # Indigo
        '#14b8a6',  # Teal
        '#ef4444',  # Red
    ]
    
    fig = go.Figure(data=[
        go.Bar(
            x=names,
            y=counts,
            marker=dict(
                color=colors[:len(names)],
                line=dict(color='white', width=2)
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
                bordercolor='#3b82f6'
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
    Uses multiple vibrant colors for each bar.
    """
    # Get destinations with average ratings
    destinations = Destination.objects.annotate(
        avg_rating=Avg('reviews__rating')
    ).filter(avg_rating__isnull=False).order_by('-avg_rating')[:10]
    
    if not destinations:
        return "<p>No data available</p>"
    
    names = [d.name for d in destinations]
    ratings = [float(d.avg_rating) for d in destinations]
    
    # Use vibrant colors for each bar
    colors = [
        '#10b981',  # Green
        '#06b6d4',  # Cyan
        '#3b82f6',  # Blue
        '#8b5cf6',  # Purple
        '#ec4899',  # Pink
        '#f97316',  # Orange
        '#f59e0b',  # Amber
        '#6366f1',  # Indigo
        '#14b8a6',  # Teal
        '#ef4444',  # Red
    ]
    
    fig = go.Figure(data=[
        go.Bar(
            x=names,
            y=ratings,
            marker=dict(
                color=colors[:len(names)],
                line=dict(color='white', width=2)
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
            textinfo='percent',
            textfont=dict(size=14, family='Arial Black'),
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
        height=650,
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.02,
            font=dict(size=11)
        )
    )
    
    return fig.to_html(full_html=False)


def generate_traveler_preferences_pie():
    """
    Generate a pie chart showing traveler preferences by favorite destination.
    Labels only shown in legend, percentages on slices.
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
            textinfo='percent',
            textfont=dict(size=14, family='Arial Black'),
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
        height=650,
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.02,
            font=dict(size=11)
        )
    )
    
    return fig.to_html(full_html=False)


def generate_rating_trends_line():
    """
    Generate a beautiful line chart showing rating trends.
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
    
    # Add scatter points for individual reviews with gradient colors
    fig.add_trace(go.Scatter(
        x=review_ids,
        y=ratings,
        mode='markers',
        name='Individual Reviews',
        marker=dict(
            size=10, 
            color=ratings,
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(
                title=dict(
                    text="Rating",
                    side="right"
                ),
                tickmode="linear",
                tick0=0,
                dtick=2
            ),
            line=dict(width=2, color='white'),
            opacity=0.8
        ),
        text=destinations,
        hovertemplate='<b>%{text}</b><br>' +
                      'Review #: %{x}<br>' +
                      'Rating: %{y}/10<br>' +
                      '<extra></extra>'
    ))
    
    # Add cumulative average line with area fill
    fig.add_trace(go.Scatter(
        x=review_ids,
        y=cumulative_avg,
        mode='lines',
        name='Cumulative Average',
        line=dict(
            color='rgba(59, 130, 246, 1)', 
            width=4,
            shape='spline'
        ),
        fill='tonexty',
        fillcolor='rgba(59, 130, 246, 0.1)',
        hovertemplate='Review #: %{x}<br>' +
                      'Average: %{y:.2f}/10<br>' +
                      '<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': 'Rating Trends Over Time',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 22, 'family': 'Arial Black', 'color': '#333'}
        },
        xaxis_title='Review Number',
        yaxis_title='Rating (0-10)',
        font=dict(family='Arial', size=13, color='#333'),
        plot_bgcolor='rgba(245, 247, 250, 0.5)',
        paper_bgcolor='white',
        height=550,
        yaxis=dict(
            range=[0, 10.5],
            gridcolor='rgba(200, 200, 200, 0.3)',
            zeroline=True,
            zerolinecolor='rgba(200, 200, 200, 0.5)'
        ),
        xaxis=dict(
            gridcolor='rgba(200, 200, 200, 0.3)'
        ),
        hovermode='closest',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            bgcolor='rgba(255, 255, 255, 0.8)',
            bordercolor='rgba(200, 200, 200, 0.5)',
            borderwidth=1
        )
    )
    
    return fig.to_html(full_html=False)


def generate_seasonal_heatmap():
    """
    Generate a beautiful heatmap showing number of visitors (reviews) per destination by month.
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
    
    # Create heatmap with vibrant color scheme
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data,
        x=months,
        y=dest_names,
        colorscale=[
            [0, '#f0f9ff'],      # Very light blue (no visitors)
            [0.2, '#bae6fd'],    # Light blue
            [0.4, '#7dd3fc'],    # Sky blue
            [0.6, '#38bdf8'],    # Bright blue
            [0.8, '#0ea5e9'],    # Deep blue
            [1, '#0369a1']       # Very deep blue (most visitors)
        ],
        showscale=True,
        colorbar=dict(
            title=dict(
                text="Visitors",
                font=dict(size=13, family='Arial Black')
            ),
            thickness=20,
            len=0.7,
            tickfont=dict(size=11)
        ),
        hovertemplate='<b>%{y}</b><br>' +
                      'Month: %{x}<br>' +
                      'Visitors: %{z}<br>' +
                      '<extra></extra>',
        xgap=2,
        ygap=2
    ))
    
    fig.update_layout(
        title={
            'text': 'Visitor Distribution by Month',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 22, 'family': 'Arial Black', 'color': '#333'}
        },
        xaxis_title='Month',
        yaxis_title='Destination',
        font=dict(family='Arial', size=13, color='#333'),
        paper_bgcolor='white',
        plot_bgcolor='white',
        height=650,
        xaxis=dict(
            tickfont=dict(size=12, family='Arial Black'),
            side='bottom'
        ),
        yaxis=dict(
            tickfont=dict(size=11),
            autorange='reversed'
        ),
        margin=dict(l=200, r=100, t=100, b=80)
    )
    
    return fig.to_html(full_html=False)


def generate_rating_distribution():
    """
    Generate a colorful histogram showing the distribution of ratings.
    """
    # Get all ratings
    reviews = Review.objects.all()
    
    if not reviews:
        return "<p>No data available</p>"
    
    ratings = [r.rating for r in reviews]
    
    # Define gradient colors for different rating ranges
    colors = [
        '#ef4444',  # Red for 0-1
        '#f97316',  # Orange for 1-2
        '#f59e0b',  # Amber for 2-3
        '#eab308',  # Yellow for 3-4
        '#84cc16',  # Lime for 4-5
        '#22c55e',  # Green for 5-6
        '#10b981',  # Emerald for 6-7
        '#14b8a6',  # Teal for 7-8
        '#06b6d4',  # Cyan for 8-9
        '#3b82f6',  # Blue for 9-10
    ]
    
    fig = go.Figure(data=[
        go.Histogram(
            x=ratings,
            nbinsx=10,
            marker=dict(
                color=colors,
                line=dict(color='white', width=2),
                opacity=0.85
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
            'font': {'size': 22, 'family': 'Arial Black', 'color': '#333'}
        },
        xaxis_title='Rating',
        yaxis_title='Frequency',
        font=dict(family='Arial', size=13, color='#333'),
        plot_bgcolor='rgba(245, 247, 250, 0.5)',
        paper_bgcolor='white',
        height=550,
        xaxis=dict(
            range=[0, 11], 
            dtick=1,
            gridcolor='rgba(200, 200, 200, 0.3)'
        ),
        yaxis=dict(
            gridcolor='rgba(200, 200, 200, 0.3)'
        ),
        bargap=0.1
    )
    
    return fig.to_html(full_html=False)


def generate_top_destinations_comparison():
    """
    Generate a multi-metric comparison chart for top destinations.
    Shows review count (horizontal) and activity count (vertical) side by side.
    """
    # Get top 8 destinations by review count
    destinations = Destination.objects.annotate(
        review_count=Count('reviews'),
        activity_count=Count('activities')
    ).order_by('-review_count')[:8]
    
    if not destinations:
        return "<p>No data available</p>"
    
    names = [d.name for d in destinations]
    reviews = [d.review_count for d in destinations]
    activities = [d.activity_count for d in destinations]
    
    # Define vibrant colors for each destination
    colors_reviews = ['#3b82f6', '#8b5cf6', '#f97316', '#10b981', '#06b6d4', '#ec4899', '#f59e0b', '#6366f1']
    colors_activities = ['#f97316', '#ec4899', '#8b5cf6', '#10b981', '#06b6d4', '#3b82f6', '#f59e0b', '#14b8a6']
    
    # Reverse names and reviews for horizontal layout (highest at top)
    names_horizontal = names[::-1]
    reviews_horizontal = reviews[::-1]
    colors_reviews_horizontal = colors_reviews[:len(names)][::-1]
    
    # Create subplots
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Reviews', 'Activities'),
        horizontal_spacing=0.15
    )
    
    # Reviews subplot - horizontal bars
    fig.add_trace(
        go.Bar(
            y=names_horizontal,
            x=reviews_horizontal,
            orientation='h',
            name='Reviews',
            marker=dict(color=colors_reviews_horizontal[:len(names_horizontal)], line=dict(color='white', width=1)),
            text=reviews_horizontal,
            textposition='outside',
            textfont=dict(size=11, family='Arial Black'),
            showlegend=False,
            hovertemplate='<b>%{y}</b><br>Reviews: %{x}<extra></extra>'
        ),
        row=1, col=1
    )
    
    # Activities subplot - vertical bars
    fig.add_trace(
        go.Bar(
            x=names,
            y=activities,
            name='Activities',
            marker=dict(color=colors_activities[:len(names)], line=dict(color='white', width=1)),
            text=activities,
            textposition='outside',
            textfont=dict(size=11, family='Arial Black'),
            showlegend=False,
            hovertemplate='<b>%{x}</b><br>Activities: %{y}<extra></extra>'
        ),
        row=1, col=2
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
        margin=dict(l=180, r=80, t=100, b=120)
    )
    
    # Update x-axes
    fig.update_xaxes(title_text="Count", row=1, col=1)
    fig.update_xaxes(tickangle=-45, tickfont=dict(size=9), row=1, col=2)
    
    # Update y-axes
    fig.update_yaxes(showticklabels=True, row=1, col=1)
    fig.update_yaxes(title_text="Count", row=1, col=2)
    
    return fig.to_html(full_html=False)

