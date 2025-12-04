"""
Juan365 Social Media Dashboard - Streamlit App
Professional analytics dashboard with Views, Reach, and Engagement metrics
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pathlib import Path

# Page config
st.set_page_config(
    page_title="Juan365 Social Media Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #4361EE 0%, #8B5CF6 100%);
        padding: 2rem;
        border-radius: 1rem;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 800;
    }
    .main-header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        text-align: center;
    }
    .stMetric {
        background: white;
        padding: 1rem;
        border-radius: 0.75rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=60)  # Cache for 60 seconds only
def load_data():
    """Load and prepare data from CSV"""
    exports_dir = Path(__file__).parent / 'exports'
    csv_files = list(exports_dir.glob('*.csv'))

    if not csv_files:
        st.error("No CSV files found in exports/ folder")
        return None

    # Get most recent CSV
    csv_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    csv_path = csv_files[0]

    df = pd.read_csv(csv_path)

    # Rename columns
    column_mapping = {
        'Post ID': 'post_id',
        'Title': 'message',
        'Publish time': 'publish_time',
        'Post type': 'post_type',
        'Permalink': 'permalink',
        'Reactions': 'reactions',
        'Comments': 'comments',
        'Shares': 'shares',
        'Views': 'views',
        'Reach': 'reach'
    }
    df = df.rename(columns=column_mapping)

    # Parse datetime
    df['publish_datetime'] = pd.to_datetime(df['publish_time'], format='%m/%d/%Y %H:%M', errors='coerce')
    df['date'] = df['publish_datetime'].dt.date
    df['hour'] = df['publish_datetime'].dt.hour
    df['day_of_week'] = df['publish_datetime'].dt.day_name()
    df['month'] = df['publish_datetime'].dt.to_period('M').astype(str)
    df['week'] = df['publish_datetime'].dt.isocalendar().week
    df['year'] = df['publish_datetime'].dt.year

    # Clean post types
    type_map = {
        'photos': 'Photo', 'photo': 'Photo',
        'videos': 'Video', 'video': 'Video',
        'reels': 'Reel', 'reel': 'Reel',
        'live': 'Live', 'live_video': 'Live', 'live stream': 'Live',
        'text': 'Text', 'status': 'Text'
    }
    df['post_type_clean'] = df['post_type'].str.lower().str.strip().map(type_map).fillna('Other')

    # Fill numeric columns
    for col in ['reactions', 'comments', 'shares', 'views', 'reach']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

    df['engagement'] = df['reactions'] + df['comments'] + df['shares']

    # Time slots
    def get_time_slot(hour):
        if 6 <= hour < 12: return 'Morning (6AM-12PM)'
        elif 12 <= hour < 18: return 'Afternoon (12PM-6PM)'
        elif 18 <= hour < 24: return 'Evening (6PM-12AM)'
        else: return 'Night (12AM-6AM)'

    df['time_slot'] = df['hour'].apply(get_time_slot)

    return df


def format_number(num):
    """Format numbers with commas, no decimals"""
    return f"{int(num):,}"


def main():
    # Load data
    df = load_data()

    if df is None:
        return

    # Header
    st.markdown("""
    <div class="main-header">
        <h1>📊 Juan365 Dashboard</h1>
        <p>Social Media Performance Analytics</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar filters
    st.sidebar.markdown("## 🎛️ Filters")

    # Date range filter
    min_date = df['date'].min()
    max_date = df['date'].max()

    date_range = st.sidebar.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    if len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = min_date, max_date

    # Post type filter
    post_types = ['All'] + sorted(df['post_type_clean'].unique().tolist())
    selected_type = st.sidebar.selectbox("Post Type", post_types)

    # Apply filters
    filtered_df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
    if selected_type != 'All':
        filtered_df = filtered_df[filtered_df['post_type_clean'] == selected_type]

    # Filter summary
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Showing:** {len(filtered_df):,} posts")
    st.sidebar.markdown(f"**Period:** {start_date} to {end_date}")

    # Main KPIs
    st.markdown("### 📈 Key Metrics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Posts", f"{len(filtered_df):,}")
    with col2:
        st.metric("Total Reach", format_number(filtered_df['reach'].sum()))
    with col3:
        st.metric("Total Views", format_number(filtered_df['views'].sum()))
    with col4:
        st.metric("Total Engagement", format_number(filtered_df['engagement'].sum()))

    col5, col6, col7, col8 = st.columns(4)

    with col5:
        avg_reach = filtered_df['reach'].mean() if len(filtered_df) > 0 else 0
        st.metric("Avg Reach/Post", format_number(avg_reach))
    with col6:
        avg_views = filtered_df['views'].mean() if len(filtered_df) > 0 else 0
        st.metric("Avg Views/Post", format_number(avg_views))
    with col7:
        st.metric("Total Reactions", format_number(filtered_df['reactions'].sum()))
    with col8:
        st.metric("Total Comments", format_number(filtered_df['comments'].sum()))

    st.markdown("---")

    # Charts row 1
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📊 Performance by Post Type")
        type_stats = filtered_df.groupby('post_type_clean').agg({
            'engagement': 'sum',
            'reach': 'sum',
            'views': 'sum',
            'post_id': 'count'
        }).rename(columns={'post_id': 'posts'}).reset_index()

        fig = px.bar(
            type_stats,
            x='post_type_clean',
            y=['reach', 'views', 'engagement'],
            title='Reach, Views & Engagement by Post Type',
            barmode='group',
            color_discrete_sequence=['#4361EE', '#06D6A0', '#EC4899']
        )
        fig.update_layout(
            xaxis_title='Post Type',
            yaxis_title='Count',
            legend_title='Metric',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### 🎯 Content Distribution")
        type_counts = filtered_df['post_type_clean'].value_counts().reset_index()
        type_counts.columns = ['Post Type', 'Count']

        fig = px.pie(
            type_counts,
            values='Count',
            names='Post Type',
            title='Posts by Type',
            color_discrete_sequence=px.colors.qualitative.Set2,
            hole=0.4
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    # Charts row 2
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📅 Daily Performance Trend")
        daily_stats = filtered_df.groupby('date').agg({
            'engagement': 'sum',
            'reach': 'sum',
            'views': 'sum'
        }).reset_index()

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=daily_stats['date'],
            y=daily_stats['reach'],
            name='Reach',
            line=dict(color='#4361EE', width=2),
            fill='tozeroy',
            fillcolor='rgba(67, 97, 238, 0.1)'
        ))
        fig.add_trace(go.Scatter(
            x=daily_stats['date'],
            y=daily_stats['views'],
            name='Views',
            line=dict(color='#06D6A0', width=2)
        ))
        fig.add_trace(go.Scatter(
            x=daily_stats['date'],
            y=daily_stats['engagement'],
            name='Engagement',
            line=dict(color='#EC4899', width=2)
        ))
        fig.update_layout(
            title='Daily Reach, Views & Engagement',
            xaxis_title='Date',
            yaxis_title='Count',
            height=400,
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### 📆 Monthly Comparison")
        monthly_stats = filtered_df.groupby('month').agg({
            'engagement': 'sum',
            'reach': 'sum',
            'views': 'sum',
            'post_id': 'count'
        }).rename(columns={'post_id': 'posts'}).reset_index()

        fig = px.bar(
            monthly_stats,
            x='month',
            y='reach',
            title='Monthly Reach',
            color_discrete_sequence=['#4361EE']
        )
        fig.update_layout(
            xaxis_title='Month',
            yaxis_title='Total Reach',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Best posting times
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📆 Best Posting Days")
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_stats = filtered_df.groupby('day_of_week').agg({
            'engagement': ['count', 'sum', 'mean'],
            'reach': 'mean',
            'views': 'mean'
        })
        day_stats.columns = ['Posts', 'Total Engagement', 'Avg Engagement', 'Avg Reach', 'Avg Views']
        day_stats = day_stats.reindex(day_order)
        day_stats = day_stats.reset_index()

        # Convert to int for clean display
        for col in ['Posts', 'Total Engagement', 'Avg Engagement', 'Avg Reach', 'Avg Views']:
            day_stats[col] = day_stats[col].fillna(0).astype(int)

        # Highlight best day
        best_day = day_stats.loc[day_stats['Avg Engagement'].idxmax(), 'day_of_week']

        st.dataframe(
            day_stats.style.highlight_max(subset=['Avg Engagement'], color='#D1FAE5').format({
                'Posts': '{:,}',
                'Total Engagement': '{:,}',
                'Avg Engagement': '{:,}',
                'Avg Reach': '{:,}',
                'Avg Views': '{:,}'
            }),
            use_container_width=True,
            hide_index=True
        )
        st.success(f"⭐ Best day: **{best_day}**")

    with col2:
        st.markdown("### ⏰ Best Posting Times")
        slot_order = ['Morning (6AM-12PM)', 'Afternoon (12PM-6PM)', 'Evening (6PM-12AM)', 'Night (12AM-6AM)']
        slot_stats = filtered_df.groupby('time_slot').agg({
            'engagement': ['count', 'sum', 'mean'],
            'reach': 'mean',
            'views': 'mean'
        })
        slot_stats.columns = ['Posts', 'Total Engagement', 'Avg Engagement', 'Avg Reach', 'Avg Views']
        slot_stats = slot_stats.reindex(slot_order)
        slot_stats = slot_stats.reset_index()

        # Convert to int for clean display
        for col in ['Posts', 'Total Engagement', 'Avg Engagement', 'Avg Reach', 'Avg Views']:
            slot_stats[col] = slot_stats[col].fillna(0).astype(int)

        # Highlight best slot
        best_slot = slot_stats.loc[slot_stats['Avg Engagement'].idxmax(), 'time_slot']

        st.dataframe(
            slot_stats.style.highlight_max(subset=['Avg Engagement'], color='#D1FAE5').format({
                'Posts': '{:,}',
                'Total Engagement': '{:,}',
                'Avg Engagement': '{:,}',
                'Avg Reach': '{:,}',
                'Avg Views': '{:,}'
            }),
            use_container_width=True,
            hide_index=True
        )
        st.success(f"⭐ Best time: **{best_slot}**")

    st.markdown("---")

    # Post Type Performance Cards
    st.markdown("### 📋 Performance by Post Type")

    type_detailed = filtered_df.groupby('post_type_clean').agg({
        'post_id': 'count',
        'engagement': ['sum', 'mean'],
        'reach': ['sum', 'mean'],
        'views': ['sum', 'mean'],
        'reactions': 'sum',
        'comments': 'sum',
        'shares': 'sum'
    }).round(0)
    type_detailed.columns = ['Posts', 'Total Engagement', 'Avg Engagement',
                             'Total Reach', 'Avg Reach', 'Total Views', 'Avg Views',
                             'Reactions', 'Comments', 'Shares']
    type_detailed = type_detailed.sort_values('Total Engagement', ascending=False).reset_index()

    # Display as cards
    cols = st.columns(min(len(type_detailed), 5))
    for i, (_, row) in enumerate(type_detailed.iterrows()):
        with cols[i % len(cols)]:
            icon = {'Photo': '📷', 'Video': '🎬', 'Reel': '🎞️', 'Live': '🔴', 'Text': '📝'}.get(row['post_type_clean'], '📄')
            st.markdown(f"""
            <div style="background: white; padding: 1rem; border-radius: 1rem; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 1rem;">
                <h3 style="margin: 0;">{icon} {row['post_type_clean']}</h3>
                <p style="color: #666; margin: 0.5rem 0;">{int(row['Posts'])} posts</p>
                <p style="margin: 0.25rem 0;"><strong>Reach:</strong> {format_number(row['Total Reach'])}</p>
                <p style="margin: 0.25rem 0;"><strong>Views:</strong> {format_number(row['Total Views'])}</p>
                <p style="margin: 0.25rem 0;"><strong>Engagement:</strong> {format_number(row['Total Engagement'])}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # Top Posts
    st.markdown("### 🏆 Top 15 Performing Posts")

    top_posts = filtered_df.nlargest(15, 'engagement')[
        ['date', 'post_type_clean', 'message', 'reach', 'views', 'reactions', 'comments', 'shares', 'engagement', 'permalink']
    ].copy()
    top_posts['message'] = top_posts['message'].fillna('').str[:80]
    top_posts.columns = ['Date', 'Type', 'Message', 'Reach', 'Views', 'Reactions', 'Comments', 'Shares', 'Engagement', 'Link']

    # Format numbers with commas
    for col in ['Reach', 'Views', 'Reactions', 'Comments', 'Shares', 'Engagement']:
        top_posts[col] = top_posts[col].apply(lambda x: f"{int(x):,}")

    st.dataframe(
        top_posts,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Link": st.column_config.LinkColumn("Link", display_text="View →"),
        }
    )

    st.markdown("---")

    # All Posts Table
    st.markdown("### 📋 All Posts")

    all_posts = filtered_df.sort_values('date', ascending=False)[
        ['date', 'post_type_clean', 'message', 'reach', 'views', 'reactions', 'comments', 'shares', 'engagement', 'permalink']
    ].copy()
    all_posts['message'] = all_posts['message'].fillna('').str[:60]
    all_posts.columns = ['Date', 'Type', 'Message', 'Reach', 'Views', 'Reactions', 'Comments', 'Shares', 'Engagement', 'Link']

    # Format numbers with commas
    for col in ['Reach', 'Views', 'Reactions', 'Comments', 'Shares', 'Engagement']:
        all_posts[col] = all_posts[col].apply(lambda x: f"{int(x):,}")

    # Add clickable links column
    all_posts['Link'] = all_posts['Link'].apply(lambda x: x if pd.notna(x) else '')

    st.dataframe(
        all_posts,
        use_container_width=True,
        height=600,
        column_config={
            "Link": st.column_config.LinkColumn("Link", display_text="View →"),
        }
    )

    # Footer
    st.markdown("---")
    st.markdown(
        f"<p style='text-align: center; color: #888;'>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')} • Data from Meta Business Suite Export</p>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
