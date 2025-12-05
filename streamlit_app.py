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
import base64

# Page config
st.set_page_config(
    page_title="Juan365 Social Media Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load logo as base64 for embedding
def get_logo_base64():
    logo_path = Path(__file__).parent / 'assets' / 'juan365_logo.jpg'
    if logo_path.exists():
        with open(logo_path, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    return None

logo_base64 = get_logo_base64()

# Custom CSS - Auto dark/light mode detection using Streamlit's native theme
st.markdown("""
<style>
    /* ===== LIGHT MODE STYLES ===== */
    /* Card styling for light mode */
    .post-type-card {
        background: #F3F4F6;
        padding: 1rem;
        border-radius: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border: 1px solid #E5E7EB;
    }
    .post-type-card h3 {
        margin: 0;
        color: #1F2937;
    }
    .post-type-card p {
        margin: 0.25rem 0;
        color: #4B5563;
    }
    .post-type-card .subtitle {
        color: #6B7280;
    }

    /* Header with logo */
    .main-header {
        background: linear-gradient(135deg, #4361EE 0%, #8B5CF6 100%);
        padding: 1.5rem 2rem;
        border-radius: 1rem;
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 1rem;
        margin-bottom: 2rem;
    }
    .main-header .logo {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        object-fit: cover;
        border: 3px solid rgba(255,255,255,0.3);
    }
    .main-header .header-text {
        text-align: left;
    }
    .main-header h1 {
        margin: 0;
        font-size: 2rem;
        font-weight: 800;
    }
    .main-header p {
        margin: 0.25rem 0 0 0;
        opacity: 0.9;
        font-size: 0.9rem;
    }

    /* Footer text - light mode */
    .footer-text {
        text-align: center;
        color: #6B7280;
        padding: 1rem;
    }

    /* ===== DARK MODE OVERRIDES ===== */
    /* Detect Streamlit dark theme */
    [data-testid="stAppViewContainer"][class*="st-emotion-cache"] {
        /* This targets all Streamlit containers */
    }

    /* Dark mode: when body/html has dark background */
    @media (prefers-color-scheme: dark) {
        .post-type-card {
            background: #262730 !important;
            border-color: #4B5563 !important;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3) !important;
        }
        .post-type-card h3 {
            color: #F9FAFB !important;
        }
        .post-type-card p {
            color: #E5E7EB !important;
        }
        .post-type-card .subtitle {
            color: #9CA3AF !important;
        }
        .footer-text {
            color: #9CA3AF !important;
        }
    }

    /* Streamlit's internal dark theme detection */
    .stApp[data-theme="dark"] .post-type-card,
    [data-theme="dark"] .post-type-card {
        background: #262730 !important;
        border-color: #4B5563 !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3) !important;
    }
    .stApp[data-theme="dark"] .post-type-card h3,
    [data-theme="dark"] .post-type-card h3 {
        color: #F9FAFB !important;
    }
    .stApp[data-theme="dark"] .post-type-card p,
    [data-theme="dark"] .post-type-card p {
        color: #E5E7EB !important;
    }
    .stApp[data-theme="dark"] .post-type-card .subtitle,
    [data-theme="dark"] .post-type-card .subtitle {
        color: #9CA3AF !important;
    }
    .stApp[data-theme="dark"] .footer-text,
    [data-theme="dark"] .footer-text {
        color: #9CA3AF !important;
    }

    /* Alternative: detect dark background color directly */
    .stApp:has([data-testid="stHeader"]) {
        /* Light mode default */
    }
</style>
""", unsafe_allow_html=True)

# Additional JavaScript-based theme detection for more reliable switching
st.markdown("""
<script>
    // Detect theme and add class to body for CSS targeting
    function detectTheme() {
        const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches ||
                       document.body.style.backgroundColor === 'rgb(14, 17, 23)' ||
                       getComputedStyle(document.body).backgroundColor === 'rgb(14, 17, 23)';
        document.body.setAttribute('data-theme', isDark ? 'dark' : 'light');
    }
    detectTheme();
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', detectTheme);
    // Re-check after Streamlit renders
    setTimeout(detectTheme, 500);
</script>
""", unsafe_allow_html=True)

# Function to get highlight color based on theme (using a moderate color that works in both)
def get_highlight_color():
    """Return a highlight color that works well in both light and dark modes"""
    # Use a teal color that's visible in both modes
    return '#0D9488'  # Teal-600 - works well on both light and dark


@st.cache_data(ttl=60)  # Cache for 60 seconds only
def load_data():
    """Load and prepare data from CSV"""
    exports_dir = Path(__file__).parent / 'exports'

    # First, try to find the merged file
    merged_file = exports_dir / 'Juan365_MERGED_ALL.csv'
    if merged_file.exists():
        csv_path = merged_file
    else:
        # Fall back to most recent CSV
        csv_files = list(exports_dir.glob('*.csv'))
        if not csv_files:
            st.error("No CSV files found in exports/ folder")
            return None
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

    # Parse datetime - Meta exports in US Pacific Time, convert to Philippine Time (+16 hours)
    df['publish_datetime'] = pd.to_datetime(df['publish_time'], format='%m/%d/%Y %H:%M', errors='coerce')
    df['publish_datetime'] = df['publish_datetime'] + pd.Timedelta(hours=16)
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

    # Time slots (adjusted for Philippine posting patterns)
    def get_time_slot(hour):
        if 6 <= hour < 12: return 'Morning (6AM-12PM)'
        elif 12 <= hour < 18: return 'Afternoon (12PM-6PM)'
        elif 18 <= hour < 22: return 'Evening (6PM-10PM)'
        else: return 'Night (10PM-6AM)'  # 22, 23, 0, 1, 2, 3, 4, 5

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

    # Header with logo
    if logo_base64:
        st.markdown(f"""
        <div class="main-header">
            <img src="data:image/jpeg;base64,{logo_base64}" class="logo" alt="Juan365 Logo">
            <div class="header-text">
                <h1>Juan365 Dashboard</h1>
                <p>Social Media Performance Analytics</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="main-header">
            <div class="header-text">
                <h1>📊 Juan365 Dashboard</h1>
                <p>Social Media Performance Analytics</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Sidebar filters
    st.sidebar.markdown("## 🎛️ Filters")

    # Quick time period filter
    today = datetime.now().date()
    min_date = df['date'].min()
    max_date = df['date'].max()

    time_periods = {
        'All Time': (min_date, max_date),
        'Today': (today, today),
        'Yesterday': (today - timedelta(days=1), today - timedelta(days=1)),
        'Last 3 Days': (today - timedelta(days=3), today),
        'Last 7 Days': (today - timedelta(days=7), today),
        'Last 14 Days': (today - timedelta(days=14), today),
        'Last 30 Days': (today - timedelta(days=30), today),
        'Last 60 Days': (today - timedelta(days=60), today),
        'Last 90 Days': (today - timedelta(days=90), today),
        'This Week': (today - timedelta(days=today.weekday()), today),
        'Last Week': (today - timedelta(days=today.weekday() + 7), today - timedelta(days=today.weekday() + 1)),
        'This Month': (today.replace(day=1), today),
        'Custom': None
    }

    selected_period = st.sidebar.selectbox("📅 Time Period", list(time_periods.keys()))

    if selected_period == 'Custom':
        date_range = st.sidebar.date_input(
            "Custom Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        if len(date_range) == 2:
            start_date, end_date = date_range
        else:
            start_date, end_date = min_date, max_date
    else:
        start_date, end_date = time_periods[selected_period]
        # Ensure dates are within data range
        start_date = max(start_date, min_date)
        end_date = min(end_date, max_date)

    # Post type filter
    post_types = ['All'] + sorted(df['post_type_clean'].unique().tolist())
    selected_type = st.sidebar.selectbox("Post Type", post_types)

    # Time slot filter
    time_slots = ['All', 'Morning (6AM-12PM)', 'Afternoon (12PM-6PM)', 'Evening (6PM-10PM)', 'Night (10PM-6AM)']
    selected_time = st.sidebar.selectbox("Time Slot", time_slots)

    # Apply filters
    filtered_df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
    if selected_type != 'All':
        filtered_df = filtered_df[filtered_df['post_type_clean'] == selected_type]
    if selected_time != 'All':
        filtered_df = filtered_df[filtered_df['time_slot'] == selected_time]

    # Filter summary
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Showing:** {len(filtered_df):,} posts")
    st.sidebar.markdown(f"**Period:** {start_date} to {end_date}")
    if selected_time != 'All':
        st.sidebar.markdown(f"**Time:** {selected_time}")

    # Main KPIs
    st.markdown("### 📈 Key Metrics")

    # Calculate metrics
    total_posts = len(filtered_df)
    total_reach = filtered_df['reach'].sum()
    total_views = filtered_df['views'].sum()
    total_engagement = filtered_df['engagement'].sum()
    avg_reach = filtered_df['reach'].mean() if total_posts > 0 else 0
    avg_views = filtered_df['views'].mean() if total_posts > 0 else 0
    total_reactions = filtered_df['reactions'].sum()
    total_comments = filtered_df['comments'].sum()

    # KPI cards row 1
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'''<div class="post-type-card">
            <p class="subtitle">📊 Total Posts</p>
            <h3>{total_posts:,}</h3>
        </div>''', unsafe_allow_html=True)
    with col2:
        st.markdown(f'''<div class="post-type-card">
            <p class="subtitle">👥 Total Reach</p>
            <h3>{format_number(total_reach)}</h3>
        </div>''', unsafe_allow_html=True)
    with col3:
        st.markdown(f'''<div class="post-type-card">
            <p class="subtitle">👁️ Total Views</p>
            <h3>{format_number(total_views)}</h3>
        </div>''', unsafe_allow_html=True)
    with col4:
        st.markdown(f'''<div class="post-type-card">
            <p class="subtitle">💬 Total Engagement</p>
            <h3>{format_number(total_engagement)}</h3>
        </div>''', unsafe_allow_html=True)

    # KPI cards row 2
    col5, col6, col7, col8 = st.columns(4)
    with col5:
        st.markdown(f'''<div class="post-type-card">
            <p class="subtitle">📈 Avg Reach/Post</p>
            <h3>{format_number(avg_reach)}</h3>
        </div>''', unsafe_allow_html=True)
    with col6:
        st.markdown(f'''<div class="post-type-card">
            <p class="subtitle">📊 Avg Views/Post</p>
            <h3>{format_number(avg_views)}</h3>
        </div>''', unsafe_allow_html=True)
    with col7:
        st.markdown(f'''<div class="post-type-card">
            <p class="subtitle">❤️ Total Reactions</p>
            <h3>{format_number(total_reactions)}</h3>
        </div>''', unsafe_allow_html=True)
    with col8:
        st.markdown(f'''<div class="post-type-card">
            <p class="subtitle">💭 Total Comments</p>
            <h3>{format_number(total_comments)}</h3>
        </div>''', unsafe_allow_html=True)

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
            day_stats.style.highlight_max(subset=['Avg Engagement'], color=get_highlight_color()).format({
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
        slot_order = ['Morning (6AM-12PM)', 'Afternoon (12PM-6PM)', 'Evening (6PM-10PM)', 'Night (10PM-6AM)']
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
            slot_stats.style.highlight_max(subset=['Avg Engagement'], color=get_highlight_color()).format({
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
            <div class="post-type-card">
                <h3>{icon} {row['post_type_clean']}</h3>
                <p class="subtitle">{int(row['Posts'])} posts</p>
                <p><strong>Reach:</strong> {format_number(row['Total Reach'])}</p>
                <p><strong>Views:</strong> {format_number(row['Total Views'])}</p>
                <p><strong>Engagement:</strong> {format_number(row['Total Engagement'])}</p>
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
        f"<p class='footer-text'>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')} • Data from Meta Business Suite Export</p>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
