from collections import defaultdict

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from django.db.models import Avg, Count, Sum

from .models import Activity, Destination, Review, Traveler

# -------------------------
# Global design tokens
# -------------------------
FONT_FAMILY = "Arial"
HEADING_FONT = "Arial Black"
PRIMARY = "#3b82f6"     # blue
ACCENT = "#10b981"      # emerald green
WARM = "#f97316"        # orange
SOFT_BG = "#f8fafc"
TEXT = "#1f2937"
SEASONS_COLORS = {
    "Spring": "#86efac",
    "Summer": "#facc15",
    "Autumn": "#f97316",
    "Fall": "#f97316",
    "Winter": "#38bdf8",
    # fallback for unknown seasons
    "Other": "#c7d2fe"
}

# Helpful default plotly qualitative palettes
PALETTE_BLUES = px.colors.sequential.Blues
PALETTE_TEALS = px.colors.sequential.Teal
PALETTE_PURPLES = px.colors.sequential.Purples
PALETTE_SET3 = px.colors.qualitative.Set3


# SAMPLE data to render visuals exactly as provided when DB data is missing
SAMPLE_DATA = {
    "destinations": ["Paris", "Tokyo", "Bali", "New York", "Nairobi"],
    "review_counts": [45, 30, 25, 35, 20],
    "avg_ratings": [9.0, 8.8, 8.5, 8.0, 7.5],
    "activities_per_destination": [12, 8, 15, 10, 6],
    "avg_activity_costs": [60, 80, 50, 100, 40],
    "traveler_favorites": {"labels": ["Paris", "Tokyo", "Bali", "New York", "Nairobi"], "values": [40, 25, 20, 10, 5]},
    "rating_buckets": {"1–3": 10, "4–6": 25, "7–10": 65},
    "season_counts": {"Spring": 10, "Summer": 18, "Autumn": 6, "Winter": 4},
    "activity_distribution": {"Tours": 40, "Hiking": 25, "Wildlife": 20, "City": 10, "Other": 5},
    "ratings_heatmap": {
        "travelers": ["Alice", "Ben", "Chloe", "Dan"],
        "matrix": [
            [8, 4, 7, 4],
            [5, 4, 8, 8],
            [5, 9, 8, 8],
            [5, 4, 7, 4],
            [7, 9, 6, 9],
        ],
    },
}


def get_analytics_summary():
    """
    Get summary metrics used in a small KPI area of the dashboard.
    """
    summary = {
        "total_destinations": Destination.objects.count(),
        "total_reviews": Review.objects.count(),
        "total_activities": Activity.objects.count(),
        "total_travelers": Traveler.objects.count(),
        "avg_rating": Review.objects.aggregate(avg=Avg("rating"))["avg"] or 0,
    }
    return summary


# 1) Top Destinations by Number of Reviews
def generate_destination_popularity_bar():
    """
    Bar chart: Top destinations by number of reviews.
    Professional teal/blue gradient, horizontal-friendly layout for many names.
    """
    # show fewer top destinations so bars are larger and easier to read
    destinations = Destination.objects.annotate(review_count=Count("reviews")).order_by("-review_count")[:5]
    if not destinations:
        names = SAMPLE_DATA["destinations"][:5]
        counts = SAMPLE_DATA["review_counts"][:5]
    else:
        names = [d.name for d in destinations]
        counts = [d.review_count for d in destinations]

    # Use a blue-teal gradient sampled according to length
    colors = (PALETTE_BLUES + PALETTE_TEALS)[-len(names):][::-1]

    fig = go.Figure(
        data=[
            go.Bar(
                x=counts,
                y=names,
                orientation="h",
                marker=dict(color=colors, line=dict(color="white", width=1)),
                text=counts,
                textposition="outside",
                hovertemplate="<b>%{y}</b><br>Reviews: %{x}<extra></extra>",
            )
        ]
    )

    fig.update_layout(
        title=dict(text="Top Destinations by Number of Reviews", x=0.5, font=dict(size=20, family=HEADING_FONT, color=TEXT)),
        xaxis_title="Number of Reviews",
        yaxis_title="Destination",
        template=None,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor=SOFT_BG,
        font=dict(family=FONT_FAMILY, color=TEXT),
        height=560,
        width=920,
        margin=dict(l=220, r=40, t=100, b=60),
        bargap=0.35,
    )

    # reverse y order so highest is on top
    fig.update_yaxes(autorange="reversed")
    return fig.to_html(full_html=False)


# 2) Average Ratings per Destination
def generate_destination_ratings_bar():
    """
    Horizontal bar chart: average rating per destination.
    Uses green->yellow->red gradient to indicate high/low satisfaction.
    """
    # show fewer destinations to keep bars larger and clearer
    destinations = Destination.objects.annotate(avg_rating=Avg("reviews__rating")).filter(avg_rating__isnull=False).order_by("-avg_rating")[:6]
    if not destinations:
        names = SAMPLE_DATA["destinations"][:6]
        ratings = SAMPLE_DATA["avg_ratings"][:6]
    else:
        names = [d.name for d in destinations]
        ratings = [float(d.avg_rating) for d in destinations]

    # create distinct colors per bar by mapping rating to a sequential palette
    palette = px.colors.sequential.Viridis

    def rating_to_color(r):
        # normalize 0..10 -> palette index
        try:
            rv = float(r)
        except Exception:
            rv = 0.0
        rv = max(0.0, min(10.0, rv))
        idx = int((rv / 10.0) * (len(palette) - 1))
        return palette[idx]

    colors = [rating_to_color(r) for r in ratings]

    # Vertical bar chart: destination on x-axis, rating on y-axis
    fig = go.Figure(
        data=[
            go.Bar(
                x=names,
                y=ratings,
                marker=dict(color=colors, line=dict(color="white", width=1)),
                text=[f"{r:.1f}" for r in ratings],
                textposition="outside",
                hovertemplate="<b>%{x}</b><br>Average Rating: %{y:.1f}/10<extra></extra>",
            )
        ]
    )

    fig.update_layout(
        title=dict(text="Average Ratings per Destination", x=0.5, font=dict(size=20, family=HEADING_FONT, color=TEXT)),
        xaxis=dict(title="Destination", tickangle=-45),
        yaxis=dict(title="Average Rating (0-10)", range=[0, 10], dtick=1),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor=SOFT_BG,
        font=dict(family=FONT_FAMILY, color=TEXT),
        height=560,
        width=920,
        margin=dict(l=80, r=40, t=100, b=160),
        bargap=0.25,
    )

    # ensure x labels readable
    fig.update_xaxes(tickangle=-45)
    return fig.to_html(full_html=False)


# 3) Number of Travelers by Favorite Destination
def generate_traveler_preferences_pie():
    """
    Donut chart: distribution of travelers by their favorite destination.
    Uses soft purples/blues for a professional look.
    """
    travelers = (
        Traveler.objects.filter(favorite_destination__isnull=False)
        .values("favorite_destination__name")
        .annotate(count=Count("id"))
        .order_by("-count")[:12]
    )
    if not travelers:
        labels = SAMPLE_DATA["traveler_favorites"]["labels"]
        values = SAMPLE_DATA["traveler_favorites"]["values"]
    else:
        labels = [t["favorite_destination__name"] for t in travelers]
        values = [t["count"] for t in travelers]

    # reduce number of slices: show top N and group the rest into 'Other'
    top_n = 5
    # sort pairs by value descending and keep top_n
    pairs = sorted(zip(values, labels), key=lambda p: p[0], reverse=True)
    top_pairs = pairs[:top_n]
    rest_pairs = pairs[top_n:]
    if rest_pairs:
        other_value = sum(p[0] for p in rest_pairs)
        top_pairs.append((other_value, "Other"))
    # unzip back into values/labels (preserve top order)
    values = [p[0] for p in top_pairs]
    labels = [p[1] for p in top_pairs]

    # use purples palette sampled to new length
    colors = (PALETTE_PURPLES + PALETTE_SET3)[: len(labels)]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.4,
                marker=dict(colors=colors, line=dict(color="white", width=0.5)),
                textinfo="percent",
                hovertemplate="%{label}: %{value}<extra></extra>",
                showlegend=True,
            )
        ]
    )

    fig.update_layout(
        title=dict(text="Traveler Favorite Destinations", x=0.5, font=dict(size=18, family=HEADING_FONT, color=TEXT)),
        paper_bgcolor=SOFT_BG,
        font=dict(family=FONT_FAMILY, color=TEXT),
        height=520,
        width=720,
        margin=dict(l=40, r=40, t=80, b=60),
        legend=dict(orientation="h", y=-0.12, x=0.5, xanchor="center", font=dict(size=11)),
    )

    return fig.to_html(full_html=False)


# Activity distribution (used by views.analytics_dashboard)
def generate_activity_distribution_pie():
    """
    Pie chart: distribution of activities.
    Groups by a sensible activity field (category/activity_type/type) and
    falls back to grouping by destination name if no activity-level category exists.
    Returns an HTML fragment.
    """
    first_act = Activity.objects.first()
    if not first_act:
        # fall back to sample distribution
        labels = list(SAMPLE_DATA["activity_distribution"].keys())
        values = list(SAMPLE_DATA["activity_distribution"].values())
        # limit slices to top N and group rest into Other
        top_n = 5
        pairs = sorted(zip(values, labels), key=lambda p: p[0], reverse=True)
        top_pairs = pairs[:top_n]
        rest_pairs = pairs[top_n:]
        if rest_pairs:
            other_value = sum(p[0] for p in rest_pairs)
            top_pairs.append((other_value, "Other"))
        values = [p[0] for p in top_pairs]
        labels = [p[1] for p in top_pairs]

        colors = (PALETTE_SET3 + PALETTE_PURPLES)[: len(labels)]

        fig = go.Figure(
            data=[
                go.Pie(
                    labels=labels,
                    values=values,
                    hole=0.35,
                    marker=dict(colors=colors, line=dict(color="white", width=1)),
                    textinfo="percent",
                    hovertemplate="<b>%{label}</b><br>Activities: %{value} (%{percent})<extra></extra>",
                )
            ]
        )

        fig.update_layout(
            title=dict(text="Activity Distribution", x=0.5, font=dict(size=18, family=HEADING_FONT, color=TEXT)),
            paper_bgcolor=SOFT_BG,
            font=dict(family=FONT_FAMILY, color=TEXT),
            height=440,
            margin=dict(l=40, r=160, t=100, b=40),
            legend=dict(orientation="v", y=0.5, x=1.02),
        )

        return fig.to_html(full_html=False)

    # choose a grouping field that exists on the Activity model (fall back to destination)
    if hasattr(first_act, "category"):
        group_field = "category"
        label_key = "category"
    elif hasattr(first_act, "activity_type"):
        group_field = "activity_type"
        label_key = "activity_type"
    elif hasattr(first_act, "type"):
        group_field = "type"
        label_key = "type"
    else:
        group_field = "destination__name"
        label_key = "destination__name"

    qs = Activity.objects.values(group_field).annotate(count=Count("id")).order_by("-count")[:12]
    if not qs:
        return "<p>No activity distribution data available</p>"

    labels = [item.get(label_key) or "Unknown" for item in qs]
    values = [item["count"] for item in qs]

    # reduce number of slices and group others into 'Other'
    top_n = 5
    pairs = sorted(zip(values, labels), key=lambda p: p[0], reverse=True)
    top_pairs = pairs[:top_n]
    rest_pairs = pairs[top_n:]
    if rest_pairs:
        other_value = sum(p[0] for p in rest_pairs)
        top_pairs.append((other_value, "Other"))
    values = [p[0] for p in top_pairs]
    labels = [p[1] for p in top_pairs]

    colors = (PALETTE_SET3 + PALETTE_PURPLES)[: len(labels)]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.35,
                marker=dict(colors=colors, line=dict(color="white", width=0.5)),
                textinfo="percent",
                hovertemplate="%{label}: %{value}<extra></extra>",
                showlegend=True,
            )
        ]
    )

    fig.update_layout(
        title=dict(text="Activity Distribution", x=0.5, font=dict(size=18, family=HEADING_FONT, color=TEXT)),
        paper_bgcolor=SOFT_BG,
        font=dict(family=FONT_FAMILY, color=TEXT),
        height=520,
        width=720,
        margin=dict(l=40, r=40, t=80, b=60),
        legend=dict(orientation="h", y=-0.12, x=0.5, xanchor="center", font=dict(size=11)),
    )

    return fig.to_html(full_html=False)


# 4) Average Activity Cost per Destination
def generate_avg_activity_cost_bar():
    """
    Bar chart: average activity cost per destination (useful for budgeting).
    If cost_estimate is missing for activities, those activities are ignored.
    """
    data = (
        Activity.objects.filter(cost_estimate__isnull=False)
        .values("destination__name")
        .annotate(avg_cost=Avg("cost_estimate"), count=Count("id"))
        .order_by("-avg_cost")[:12]
    )
    if not data:
        names = SAMPLE_DATA["destinations"]
        avg_costs = SAMPLE_DATA["avg_activity_costs"]
        counts = SAMPLE_DATA["activities_per_destination"]
    else:
        names = [d["destination__name"] for d in data]
        avg_costs = [float(d["avg_cost"]) for d in data]
        counts = [d["count"] for d in data]

    colors = [ACCENT if c < 5 else PRIMARY for c in counts]  # cheaper destinations get accent, many-activity destinations get primary

    fig = go.Figure(
        data=[
            go.Bar(
                x=names,
                y=avg_costs,
                marker=dict(color=colors, line=dict(color="white", width=1)),
                text=[f"${c:,.0f}" for c in avg_costs],
                textposition="outside",
                hovertemplate="<b>%{x}</b><br>Avg Activity Cost: $%{y:.2f}<br>Number of Activities: %{customdata}<extra></extra>",
                customdata=counts,
            )
        ]
    )

    fig.update_layout(
        title=dict(text="Average Activity Cost per Destination", x=0.5, font=dict(size=18, family=HEADING_FONT, color=TEXT)),
        xaxis_title="Destination",
        yaxis_title="Average Cost (USD)",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor=SOFT_BG,
        font=dict(family=FONT_FAMILY, color=TEXT),
        height=480,
        margin=dict(l=80, r=40, t=100, b=120),
    )

    fig.update_xaxes(tickangle=-45)
    return fig.to_html(full_html=False)


# 5) Best Seasons to Visit (Distribution)
def generate_best_season_distribution():
    """
    Column chart or pie chart showing distribution of 'best_season' values across destinations.
    Handles common season text (Spring, Summer, Autumn/Fall, Winter) and groups others into 'Other'.
    """
    raw = Destination.objects.values_list("best_season", flat=True)
    if not raw:
        # use sample season counts
        counts = SAMPLE_DATA["season_counts"].copy()
    else:
        counts = defaultdict(int)
        for s in raw:
            if not s:
                counts["Other"] += 1
                continue
            key = s.strip().title()
            # normalize Autumn / Fall
            if key in ("Fall",):
                key = "Autumn"
            if key not in SEASONS_COLORS:
                key = "Other"
            counts[key] += 1

    labels = list(counts.keys())
    values = [counts[k] for k in labels]
    colors = [SEASONS_COLORS.get(k, SEASONS_COLORS["Other"]) for k in labels]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.35,
                marker=dict(colors=colors, line=dict(color="white", width=1)),
                textinfo="percent+label",
                hovertemplate="%{label}: %{value} destinations (%{percent})<extra></extra>",
            )
        ]
    )

    fig.update_layout(
        title=dict(text="Best Seasons to Visit (Distribution)", x=0.5, font=dict(size=18, family=HEADING_FONT, color=TEXT)),
        paper_bgcolor=SOFT_BG,
        font=dict(family=FONT_FAMILY, color=TEXT),
        height=480,
        margin=dict(l=40, r=160, t=100, b=40),
    )

    return fig.to_html(full_html=False)


# 6) Traveler Ratings Distribution
def generate_rating_distribution():
    """
    Pie chart showing bucketed rating distribution across all reviews.
    Buckets: 1-3, 4-6, 7-10 to match dashboard visuals.
    """
    reviews = Review.objects.all()
    if not reviews:
        labels = list(SAMPLE_DATA["rating_buckets"].keys())
        values = list(SAMPLE_DATA["rating_buckets"].values())
    else:
        # Bucket ratings into 3 groups: 1-3, 4-6, 7-10
        buckets = {"1–3": 0, "4–6": 0, "7–10": 0}
        for r in reviews:
            try:
                val = int(r.rating)
            except Exception:
                continue
            if val <= 3:
                buckets["1–3"] += 1
            elif val <= 6:
                buckets["4–6"] += 1
            else:
                buckets["7–10"] += 1

        labels = list(buckets.keys())
        values = [buckets[k] for k in labels]

    colors = ["#ff6b6b", "#facc15", "#10b981"]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.35,
                marker=dict(colors=colors, line=dict(color="white", width=1)),
                textinfo="percent",
                hovertemplate="%{label}: %{value} reviews (%{percent})<extra></extra>",
            )
        ]
    )

    fig.update_layout(
        title=dict(text="Review Rating Distribution", x=0.5, font=dict(size=18, family=HEADING_FONT, color=TEXT)),
        paper_bgcolor=SOFT_BG,
        font=dict(family=FONT_FAMILY, color=TEXT),
        height=520,
        margin=dict(l=40, r=40, t=100, b=40),
    )

    return fig.to_html(full_html=False)


# 7) Top 5 Activities by Popularity or Cost
def generate_top_activities_bar(by="popularity"):
    """
    Bar chart of the top activities.
    - by="popularity" uses number of reviews linked to the activity's destination as a proxy.
    - by="cost" sorts by average cost (highest first).
    Returns top 5 activities.
    """
    # attempt popularity: count reviews for the activity's destination as proxy for activity popularity
    if by == "popularity":
        # annotate with number of reviews at destination
        data = (
            Activity.objects.annotate(popularity=Count("destination__reviews"))
            .order_by("-popularity")[:5]
        )
        if not data:
            # fallback to sample using destination review counts
            names = [f"Popular Activity — {d}" for d in SAMPLE_DATA["destinations"]]
            values = SAMPLE_DATA["review_counts"]
        else:
            names = [f"{a.name} — {a.destination.name}" for a in data]
            values = [a.popularity for a in data]
        colors = PALETTE_SET3[: len(names)]

        fig = go.Figure(
            data=[
                go.Bar(
                    x=names,
                    y=values,
                    marker=dict(color=colors, line=dict(color="white", width=1)),
                    text=values,
                    textposition="outside",
                    hovertemplate="<b>%{x}</b><br>Popularity proxy (dest reviews): %{y}<extra></extra>",
                )
            ]
        )

        fig.update_layout(
            title=dict(text="Top 5 Activities by Popularity (proxy)", x=0.5, font=dict(size=18, family=HEADING_FONT, color=TEXT)),
            xaxis=dict(title="", tickangle=-45),
            yaxis=dict(title="Popularity (destination reviews)"),
            paper_bgcolor=SOFT_BG,
            font=dict(family=FONT_FAMILY, color=TEXT),
            height=480,
            margin=dict(l=80, r=40, t=100, b=160),
        )

        return fig.to_html(full_html=False)

    # by cost
    data = Activity.objects.filter(cost_estimate__isnull=False).order_by("-cost_estimate")[:5]
    if not data:
        names = [f"Activity — {d}" for d in SAMPLE_DATA["destinations"]]
        costs = SAMPLE_DATA["avg_activity_costs"]
    else:
        names = [f"{a.name} — {a.destination.name}" for a in data]
        costs = [float(a.cost_estimate) for a in data]
    colors = ["#fbbf24", "#8b5cf6", "#a855f7", "#f97316", "#06b6d4"][: len(names)]

    fig = go.Figure(
        data=[
            go.Bar(
                x=names,
                y=costs,
                marker=dict(color=colors, line=dict(color="white", width=1)),
                text=[f"${c:,.0f}" for c in costs],
                textposition="outside",
                hovertemplate="<b>%{x}</b><br>Cost: $%{y:.2f}<extra></extra>",
            )
        ]
    )

    fig.update_layout(
        title=dict(text="Top 5 Activities by Cost", x=0.5, font=dict(size=18, family=HEADING_FONT, color=TEXT)),
        xaxis=dict(title="", tickangle=-45),
        yaxis=dict(title="Cost (USD)"),
        paper_bgcolor=SOFT_BG,
        font=dict(family=FONT_FAMILY, color=TEXT),
        height=480,
        margin=dict(l=80, r=40, t=100, b=160),
    )

    return fig.to_html(full_html=False)


# 8) Interactive Map Visualization (Optional, advanced)
def generate_interactive_map():
    """
    Interactive map showing destinations.
    Requires Destination model to have latitude & longitude fields:
    - latitude (float) and longitude (float)
    If those fields are not present or no coords exist, returns an explanatory message.
    """
    # Attempt to fetch lat/lon fields dynamically; if not available, gracefully return message
    sample = Destination.objects.first()
    if not sample:
        return "<p>No destinations available</p>"

    has_lat = hasattr(sample, "latitude")
    has_lon = hasattr(sample, "longitude")
    if not (has_lat and has_lon):
        return "<p>Interactive map requires `latitude` and `longitude` fields on the Destination model.</p>"

    # collect destinations with coords
    qs = Destination.objects.exclude(latitude__isnull=True).exclude(longitude__isnull=True)
    if not qs:
        return "<p>No geolocation data available on destinations.</p>"

    df = []
    for d in qs:
        try:
            lat = float(d.latitude)
            lon = float(d.longitude)
        except Exception:
            continue
        df.append(
            {
                "name": d.name,
                "lat": lat,
                "lon": lon,
                "avg_rating": d.reviews.aggregate(avg=Avg("rating"))["avg"] or 0,
                "num_reviews": d.reviews.count(),
            }
        )

    if not df:
        return "<p>No valid coordinate data available</p>"

    # build scatter_geo
    lats = [r["lat"] for r in df]
    lons = [r["lon"] for r in df]
    names = [r["name"] for r in df]
    ratings = [r["avg_rating"] for r in df]
    sizes = [max(8, min(30, r["num_reviews"] * 0.6 + 6)) for r in df]  # size by number of reviews

    fig = px.scatter_geo(
        df,
        lat="lat",
        lon="lon",
        hover_name="name",
        size="num_reviews",
        size_max=30,
        projection="natural earth",
        title="Destinations Map (click marker for details)",
        color=ratings,
        color_continuous_scale=px.colors.sequential.Viridis,
        labels={"color": "Avg Rating"},
    )

    fig.update_traces(
        marker=dict(line=dict(width=0.5, color="white")),
        hovertemplate="<b>%{hovertext}</b><br>Avg Rating: %{marker.color:.1f}<br>Reviews: %{marker.size}<extra></extra>",
    )

    fig.update_layout(
        paper_bgcolor=SOFT_BG,
        font=dict(family=FONT_FAMILY, color=TEXT),
        height=600,
        margin=dict(l=40, r=40, t=100, b=40),
        coloraxis_colorbar=dict(title="Avg Rating"),
    )

    return fig.to_html(full_html=False)


# 6) Rating trends over time (monthly average)
def generate_rating_trends_line():
    """
    Line chart: monthly average rating across all reviews.
    Returns an HTML fragment (fig.to_html(full_html=False)) or a small
    explanatory string when no data is available.
    """
    # ensure reviews have a timestamp
    reviews = Review.objects.filter(created_at__isnull=False).order_by("created_at")
    if not reviews:
        return "<p>No data available</p>"

    # group ratings by YYYY-MM
    monthly = defaultdict(list)
    for r in reviews:
        try:
            key = r.created_at.strftime("%Y-%m")
        except Exception:
            # skip records with invalid dates
            continue
        monthly[key].append(r.rating)

    if not monthly:
        return "<p>No data available</p>"

    labels = sorted(monthly.keys())
    avg_ratings = [sum(monthly[k]) / len(monthly[k]) for k in labels]

    fig = go.Figure(
        data=[
            go.Scatter(
                x=labels,
                y=avg_ratings,
                mode="lines+markers",
                line=dict(color=PRIMARY, width=2),
                marker=dict(size=6, color=PRIMARY),
                hovertemplate="%{x}<br>Avg Rating: %{y:.2f}<extra></extra>",
            )
        ]
    )

    fig.update_layout(
        title=dict(text="Rating Trends (monthly average)", x=0.5, font=dict(size=18, family=HEADING_FONT, color=TEXT)),
        xaxis=dict(title="Month", tickangle=-45),
        yaxis=dict(title="Average Rating (0-10)", range=[0, 10], dtick=1),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor=SOFT_BG,
        font=dict(family=FONT_FAMILY, color=TEXT),
        height=420,
        margin=dict(l=80, r=40, t=100, b=140),
    )

    return fig.to_html(full_html=False)


def generate_seasonal_heatmap():
    """
    Heatmap showing counts of destinations by country (rows) and best season (columns).
    Uses the top countries by number of destinations to keep the chart readable.
    Returns an HTML fragment or small message when no data is available.
    """
    # collect raw destination best_season and country
    qs = Destination.objects.values("country", "best_season")
    if not qs:
        return "<p>No destination data available</p>"

    # determine top countries by destination count
    country_counts = (
        Destination.objects.values("country").annotate(cnt=Count("id")).order_by("-cnt")[:8]
    )
    top_countries = [c["country"] for c in country_counts]
    if not top_countries:
        return "<p>No country data available</p>"

    seasons = ["Spring", "Summer", "Autumn", "Winter", "Other"]

    # build matrix of counts
    matrix = []
    for country in top_countries:
        row = []
        for season in seasons:
            # normalize season values like in other functions
            raw = Destination.objects.filter(country=country).values_list("best_season", flat=True)
            c = 0
            for s in raw:
                if not s:
                    key = "Other"
                else:
                    key = s.strip().title()
                    if key in ("Fall",):
                        key = "Autumn"
                    if key not in SEASONS_COLORS:
                        key = "Other"
                if key == season:
                    c += 1
            row.append(c)
        matrix.append(row)

    # if matrix empty or all zeros, return message
    if not any(sum(r) for r in matrix):
        return "<p>No season/country distribution data available</p>"

    fig = go.Figure(
        data=[
            go.Heatmap(
                z=matrix,
                x=seasons,
                y=top_countries,
                colorscale="Blues",
                hovertemplate="%{y} — %{x}: %{z} destinations<extra></extra>",
            )
        ]
    )

    fig.update_layout(
        title=dict(text="Destinations by Country and Best Season", x=0.5, font=dict(size=16, family=HEADING_FONT, color=TEXT)),
        xaxis=dict(title="Season"),
        yaxis=dict(title="Country"),
        paper_bgcolor=SOFT_BG,
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT_FAMILY, color=TEXT),
        height=520,
        margin=dict(l=140, r=40, t=80, b=80),
    )

    return fig.to_html(full_html=False)


def generate_top_destinations_comparison():
    """
    Comparison chart for top destinations showing review count (bar) and
    average rating (line) using a secondary y-axis.
    Returns HTML fragment.
    """
    data = (
        Destination.objects.annotate(review_count=Count("reviews"), avg_rating=Avg("reviews__rating"))
        .order_by("-review_count")[:6]
    )
    if not data:
        names = SAMPLE_DATA["destinations"]
        counts = SAMPLE_DATA["review_counts"]
        avg_ratings = SAMPLE_DATA["avg_ratings"]
    else:
        names = [d.name for d in data]
        counts = [d.review_count for d in data]
        avg_ratings = [float(d.avg_rating or 0) for d in data]

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Bar(x=names, y=counts, name="Reviews", marker=dict(color=PALETTE_BLUES[-len(names):])),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=names, y=avg_ratings, name="Avg Rating", mode="lines+markers", marker=dict(color=ACCENT, size=8)),
        secondary_y=True,
    )

    fig.update_layout(
        title=dict(text="Top Destinations: Reviews vs Avg Rating", x=0.5, font=dict(size=16, family=HEADING_FONT, color=TEXT)),
        paper_bgcolor=SOFT_BG,
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT_FAMILY, color=TEXT),
        height=480,
        margin=dict(l=80, r=80, t=100, b=160),
        legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"),
    )

    fig.update_yaxes(title_text="Number of Reviews", secondary_y=False)
    fig.update_yaxes(title_text="Avg Rating (0-10)", range=[0, 10], secondary_y=True)

    return fig.to_html(full_html=False)


def generate_activities_per_destination_bar():
    """
    Bar chart: number of activities per destination (top 6 destinations).
    Useful to show how activity-rich each destination is.
    """
    data = (
        Activity.objects.values("destination__name")
        .annotate(count=Count("id"))
        .order_by("-count")[:6]
    )
    if not data:
        names = SAMPLE_DATA["destinations"]
        counts = SAMPLE_DATA["activities_per_destination"]
    else:
        names = [d["destination__name"] for d in data]
        counts = [d["count"] for d in data]

    colors = PALETTE_PURPLES[-len(names):]

    fig = go.Figure(
        data=[
            go.Bar(
                x=names,
                y=counts,
                marker=dict(color=colors, line=dict(color="white", width=1)),
                text=counts,
                textposition="outside",
                hovertemplate="%{x}: %{y} activities<extra></extra>",
            )
        ]
    )

    fig.update_layout(
        title=dict(text="Activities per Destination", x=0.5, font=dict(size=18, family=HEADING_FONT, color=TEXT)),
        xaxis_title="Destination",
        yaxis_title="Number of Activities",
        paper_bgcolor=SOFT_BG,
        font=dict(family=FONT_FAMILY, color=TEXT),
        height=480,
        margin=dict(l=80, r=40, t=100, b=120),
    )

    return fig.to_html(full_html=False)


def generate_ratings_heatmap(top_destinations=6, top_travelers=6):
    """
    Heatmap matrix of average ratings per (destination, traveler).
    Selects top destinations and travelers by review count to keep the chart small.
    Returns HTML fragment.
    """
    # pick top destinations by review count
    dests_qs = Destination.objects.annotate(review_count=Count("reviews")).order_by("-review_count")[:top_destinations]
    travelers_by_reviews = (
        Review.objects.values("traveler__id", "traveler__name").annotate(cnt=Count("id")).order_by("-cnt")[:top_travelers]
    )

    # fallback to sample if not enough data
    if not dests_qs or not travelers_by_reviews:
        dests = SAMPLE_DATA["destinations"]
        travelers = SAMPLE_DATA["ratings_heatmap"]["travelers"]
        matrix = SAMPLE_DATA["ratings_heatmap"]["matrix"]
    else:
        dests = [d.name for d in dests_qs]
        travelers = [t["traveler__name"] for t in travelers_by_reviews]

        # build matrix of avg ratings
        matrix = []
        for d in dests_qs:
            row = []
            for t in travelers_by_reviews:
                avg = (
                    Review.objects.filter(destination=d, traveler__id=t["traveler__id"]).aggregate(avg=Avg("rating"))["avg"]
                )
                row.append(float(avg) if avg is not None else None)
            matrix.append(row)

    # if all None, return message
    if not any(any(cell is not None for cell in row) for row in matrix):
        return "<p>No ratings matrix data available</p>"

    fig = go.Figure(
        data=[
            go.Heatmap(
                z=matrix,
                x=travelers,
                y=dests,
                colorscale="Teal",
                colorbar=dict(title="Rating"),
                zmin=1,
                zmax=10,
                hovertemplate="%{y} — %{x}: %{z}<extra></extra>",
            )
        ]
    )

    # add annotations (numbers) where present
    annotations = []
    for yi, row in enumerate(matrix):
        for xi, val in enumerate(row):
            text = "" if val is None else f"{val:.0f}"
            annotations.append(
                dict(x=travelers[xi], y=dests[yi], text=text, showarrow=False, font=dict(color="black"))
            )
    fig.update_layout(
        title=dict(text="Ratings Heatmap (Destination vs Traveler)", x=0.5, font=dict(size=16, family=HEADING_FONT, color=TEXT)),
        paper_bgcolor=SOFT_BG,
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT_FAMILY, color=TEXT),
        height=520,
        margin=dict(l=140, r=80, t=100, b=120),
        annotations=annotations,
    )

    return fig.to_html(full_html=False)