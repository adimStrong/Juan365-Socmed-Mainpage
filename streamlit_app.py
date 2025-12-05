"""
Juan365 Social Media Dashboard - Streamlit App
Professional analytics dashboard powered by Facebook Graph API
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pathlib import Path
import base64
import json
import requests

# Try to load config - supports both local config.py and Streamlit secrets
def get_credentials():
    """Get API credentials from config.py or Streamlit secrets"""
    try:
        from config import PAGE_ID, PAGE_TOKEN, BASE_URL
        return PAGE_ID, PAGE_TOKEN, BASE_URL
    except ImportError:
        # Running on Streamlit Cloud - use secrets
        try:
            page_id = st.secrets["PAGE_ID"]
            page_token = st.secrets["PAGE_TOKEN"]
            base_url = st.secrets.get("BASE_URL", "https://graph.facebook.com/v21.0")
            return page_id, page_token, base_url
        except Exception as e:
            st.warning(f"No credentials found. Please add secrets in Streamlit Cloud settings.")
            return None, None, "https://graph.facebook.com/v21.0"

# These will be set when needed
PAGE_ID, PAGE_TOKEN, BASE_URL = None, None, "https://graph.facebook.com/v21.0"

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

# Custom CSS
st.markdown("""
<style>
    .post-type-card {
        background: #F3F4F6;
        padding: 1rem;
        border-radius: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border: 1px solid #E5E7EB;
    }
    .post-type-card h3 { margin: 0; color: #1F2937; }
    .post-type-card p { margin: 0.25rem 0; color: #4B5563; }
    .post-type-card .subtitle { color: #6B7280; }

    .page-overview-card {
        background: linear-gradient(135deg, #4361EE 0%, #8B5CF6 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        color: white;
        text-align: center;
        margin-bottom: 1rem;
    }
    .page-overview-card h2 { margin: 0; font-size: 2.5rem; }
    .page-overview-card p { margin: 0.5rem 0 0 0; opacity: 0.9; }

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
    .main-header .header-text { text-align: left; }
    .main-header h1 { margin: 0; font-size: 2rem; font-weight: 800; }
    .main-header p { margin: 0.25rem 0 0 0; opacity: 0.9; font-size: 0.9rem; }
    .footer-text { text-align: center; color: #6B7280; padding: 1rem; }

    @media (prefers-color-scheme: dark) {
        .post-type-card {
            background: #262730 !important;
            border-color: #4B5563 !important;
        }
        .post-type-card h3 { color: #F9FAFB !important; }
        .post-type-card p { color: #E5E7EB !important; }
        .post-type-card .subtitle { color: #9CA3AF !important; }
        .footer-text { color: #9CA3AF !important; }
    }
</style>
""", unsafe_allow_html=True)


def get_highlight_color():
    return '#0D9488'


# ===== API FETCH FUNCTIONS (for Streamlit Cloud) =====
@st.cache_data(ttl=300)
def fetch_page_info_api():
    """Fetch page-level metrics from Facebook API"""
    page_id, page_token, base_url = get_credentials()
    if not page_id or not page_token:
        return {}

    url = f"{base_url}/{page_id}"
    params = {
        'fields': 'name,fan_count,followers_count,talking_about_count,overall_star_rating,rating_count',
        'access_token': page_token
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        if 'error' not in data:
            data['fetched_at'] = datetime.now().isoformat()
            return data
    except Exception:
        pass
    return {}


@st.cache_data(ttl=300)
def fetch_posts_api(limit=100):
    """Fetch recent posts with engagement from Facebook API"""
    page_id, page_token, base_url = get_credentials()
    if not page_id or not page_token:
        return {'posts': [], 'total_posts': 0}

    posts = []
    url = f"{base_url}/{page_id}/posts"
    params = {
        'fields': 'id,message,created_time,shares,permalink_url,status_type,'
                  'reactions.type(LIKE).summary(true).as(like),'
                  'reactions.type(LOVE).summary(true).as(love),'
                  'reactions.type(HAHA).summary(true).as(haha),'
                  'reactions.type(WOW).summary(true).as(wow),'
                  'reactions.type(SAD).summary(true).as(sad),'
                  'reactions.type(ANGRY).summary(true).as(angry),'
                  'reactions.summary(true),comments.summary(true)',
        'limit': limit,
        'access_token': page_token
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        data = response.json()

        if 'error' not in data:
            for post in data.get('data', []):
                processed = {
                    'id': post.get('id'),
                    'message': post.get('message', '')[:200] if post.get('message') else '',
                    'created_time': post.get('created_time'),
                    'permalink_url': post.get('permalink_url'),
                    'post_type': post.get('status_type', 'unknown'),
                    'reactions': post.get('reactions', {}).get('summary', {}).get('total_count', 0),
                    'comments': post.get('comments', {}).get('summary', {}).get('total_count', 0),
                    'shares': post.get('shares', {}).get('count', 0) if post.get('shares') else 0,
                    'like': post.get('like', {}).get('summary', {}).get('total_count', 0),
                    'love': post.get('love', {}).get('summary', {}).get('total_count', 0),
                    'haha': post.get('haha', {}).get('summary', {}).get('total_count', 0),
                    'wow': post.get('wow', {}).get('summary', {}).get('total_count', 0),
                    'sad': post.get('sad', {}).get('summary', {}).get('total_count', 0),
                    'angry': post.get('angry', {}).get('summary', {}).get('total_count', 0),
                }
                processed['engagement'] = processed['reactions'] + processed['comments'] + processed['shares']
                posts.append(processed)
    except Exception:
        pass

    return {
        'fetched_at': datetime.now().isoformat(),
        'total_posts': len(posts),
        'posts': posts
    }


@st.cache_data(ttl=300)
def fetch_videos_api(limit=100):
    """Fetch videos with view counts from Facebook API"""
    page_id, page_token, base_url = get_credentials()
    if not page_id or not page_token:
        return {'videos': [], 'total_videos': 0, 'total_views': 0}

    videos = []
    url = f"{base_url}/{page_id}/videos"
    params = {
        'fields': 'id,title,description,created_time,length,views,permalink_url',
        'limit': limit,
        'access_token': page_token
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        data = response.json()

        if 'error' not in data:
            videos = data.get('data', [])
    except Exception:
        pass

    total_views = sum(v.get('views', 0) for v in videos)
    return {
        'fetched_at': datetime.now().isoformat(),
        'total_videos': len(videos),
        'total_views': total_views,
        'videos': videos
    }


@st.cache_data(ttl=60)
def load_api_data():
    """Load data from API JSON files or fetch from API directly"""
    data_dir = Path(__file__).parent / 'data'

    # Load page info from file
    page_info = {}
    page_info_file = data_dir / 'page_info.json'
    if page_info_file.exists():
        with open(page_info_file, 'r', encoding='utf-8') as f:
            page_info = json.load(f)

    # Load posts from file
    posts_data = {'posts': [], 'total_posts': 0}
    posts_file = data_dir / 'posts.json'
    if posts_file.exists():
        with open(posts_file, 'r', encoding='utf-8') as f:
            posts_data = json.load(f)

    # Load videos from file
    videos_data = {'videos': [], 'total_videos': 0, 'total_views': 0}
    videos_file = data_dir / 'videos.json'
    if videos_file.exists():
        with open(videos_file, 'r', encoding='utf-8') as f:
            videos_data = json.load(f)

    # If no local files, try fetching from API (Streamlit Cloud mode)
    page_id, page_token, _ = get_credentials()

    if not page_info and page_id and page_token:
        page_info = fetch_page_info_api()

    if not posts_data.get('posts') and page_id and page_token:
        posts_data = fetch_posts_api(limit=100)

    if not videos_data.get('videos') and page_id and page_token:
        videos_data = fetch_videos_api(limit=100)

    return page_info, posts_data, videos_data


@st.cache_data(ttl=60)
def load_csv_data():
    """Load data from CSV exports (fallback)"""
    exports_dir = Path(__file__).parent / 'exports'

    merged_file = exports_dir / 'Juan365_MERGED_ALL.csv'
    if merged_file.exists():
        csv_path = merged_file
    else:
        csv_files = list(exports_dir.glob('*.csv'))
        if not csv_files:
            return None
        csv_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        csv_path = csv_files[0]

    df = pd.read_csv(csv_path)

    column_mapping = {
        'Post ID': 'post_id', 'Title': 'message', 'Publish time': 'publish_time',
        'Post type': 'post_type', 'Permalink': 'permalink',
        'Reactions': 'reactions', 'Comments': 'comments', 'Shares': 'shares',
        'Views': 'views', 'Reach': 'reach'
    }
    df = df.rename(columns=column_mapping)

    df['publish_datetime'] = pd.to_datetime(df['publish_time'], format='%m/%d/%Y %H:%M', errors='coerce')
    df['publish_datetime'] = df['publish_datetime'] + pd.Timedelta(hours=16)
    df['date'] = df['publish_datetime'].dt.date
    df['hour'] = df['publish_datetime'].dt.hour

    for col in ['reactions', 'comments', 'shares', 'views', 'reach']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

    df['engagement'] = df['reactions'] + df['comments'] + df['shares']

    # Add Total Clicks if available
    if 'Total clicks' in df.columns:
        df['total_clicks'] = pd.to_numeric(df['Total clicks'], errors='coerce').fillna(0).astype(int)

    # Clean post type for filtering
    if 'post_type' in df.columns:
        df['post_type_clean'] = df['post_type'].fillna('Unknown').str.strip()
    else:
        df['post_type_clean'] = 'Unknown'

    # Add month column for grouping
    df['month'] = df['publish_datetime'].dt.to_period('M').astype(str)

    # Add day_of_week for best posting time analysis
    df['day_of_week'] = df['publish_datetime'].dt.day_name()

    # Add time_slot for hourly analysis
    def get_time_slot(hour):
        if 6 <= hour < 12:
            return 'Morning (6AM-12PM)'
        elif 12 <= hour < 18:
            return 'Afternoon (12PM-6PM)'
        elif 18 <= hour < 22:
            return 'Evening (6PM-10PM)'
        else:
            return 'Night (10PM-6AM)'
    df['time_slot'] = df['hour'].apply(get_time_slot)

    return df


def prepare_posts_dataframe(posts_data):
    """Convert API posts data to DataFrame"""
    posts = posts_data.get('posts', [])
    if not posts:
        return None

    df = pd.DataFrame(posts)

    # Parse datetime (API returns UTC)
    df['publish_datetime'] = pd.to_datetime(df['created_time'], errors='coerce')
    df['publish_datetime'] = df['publish_datetime'] + pd.Timedelta(hours=8)  # Convert to PHT
    df['date'] = df['publish_datetime'].dt.date
    df['hour'] = df['publish_datetime'].dt.hour
    df['day_of_week'] = df['publish_datetime'].dt.day_name()
    df['month'] = df['publish_datetime'].dt.to_period('M').astype(str)

    # Time slots
    def get_time_slot(hour):
        if 6 <= hour < 12: return 'Morning (6AM-12PM)'
        elif 12 <= hour < 18: return 'Afternoon (12PM-6PM)'
        elif 18 <= hour < 22: return 'Evening (6PM-10PM)'
        else: return 'Night (10PM-6AM)'

    df['time_slot'] = df['hour'].apply(get_time_slot)

    # Clean post types
    df['post_type_clean'] = df['post_type'].fillna('Unknown')

    return df


def format_number(num):
    """Format numbers with commas"""
    return f"{int(num):,}"


def main():
    # Load API data (for page-level info: followers, rating, video views, reaction breakdown)
    page_info, posts_data, videos_data = load_api_data()

    # PRIMARY: Load CSV data (has Reach, Views, complete engagement data)
    df = load_csv_data()

    # If no CSV, fall back to API data
    if df is None or df.empty:
        df = prepare_posts_dataframe(posts_data)
    else:
        # Merge reaction breakdown from API into CSV data
        api_posts = posts_data.get('posts', [])
        if api_posts:
            # Create a mapping of post_id to reaction data
            reaction_cols = ['like', 'love', 'haha', 'wow', 'sad', 'angry']
            api_reactions = {}
            for post in api_posts:
                # API uses full ID like "580104038511364_122169709076762707"
                # CSV might use just the second part
                post_id = post.get('id', '')
                short_id = post_id.split('_')[-1] if '_' in post_id else post_id
                api_reactions[post_id] = {col: post.get(col, 0) for col in reaction_cols}
                api_reactions[short_id] = {col: post.get(col, 0) for col in reaction_cols}

            # Add reaction columns to df if not present
            for col in reaction_cols:
                if col not in df.columns:
                    df[col] = 0

            # Match and update reaction data
            for idx, row in df.iterrows():
                csv_post_id = str(row.get('post_id', ''))
                if csv_post_id in api_reactions:
                    for col in reaction_cols:
                        df.at[idx, col] = api_reactions[csv_post_id].get(col, 0)

    # Header
    if logo_base64:
        st.markdown(f"""
        <div class="main-header">
            <img src="data:image/jpeg;base64,{logo_base64}" class="logo" alt="Juan365 Logo">
            <div class="header-text">
                <h1>Juan365 Dashboard</h1>
                <p>Social Media Performance Analytics (API Powered)</p>
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

    # ===== PAGE OVERVIEW SECTION (NEW!) =====
    st.markdown("### 🏠 Page Overview")

    # Calculate totals from API posts data
    api_posts = posts_data.get('posts', [])
    api_total_reactions = sum(p.get('reactions', 0) for p in api_posts)
    api_total_comments = sum(p.get('comments', 0) for p in api_posts)
    api_total_shares = sum(p.get('shares', 0) for p in api_posts)
    api_post_count = len(api_posts)

    col1, col2, col3 = st.columns(3)

    with col1:
        followers = page_info.get('fan_count', 0)
        st.markdown(f'''<div class="page-overview-card">
            <h2>{format_number(followers)}</h2>
            <p>👥 Followers</p>
        </div>''', unsafe_allow_html=True)

    with col2:
        rating = page_info.get('overall_star_rating', 0)
        rating_count = page_info.get('rating_count', 0)
        st.markdown(f'''<div class="page-overview-card">
            <h2>{rating}/5 ⭐</h2>
            <p>📊 Rating ({rating_count:,} reviews)</p>
        </div>''', unsafe_allow_html=True)

    with col3:
        talking_about = page_info.get('talking_about_count', 0)
        st.markdown(f'''<div class="page-overview-card">
            <h2>{format_number(talking_about)}</h2>
            <p>🔥 Talking About (Weekly)</p>
        </div>''', unsafe_allow_html=True)

    # Second row - API engagement stats
    col4, col5, col6, col7 = st.columns(4)

    with col4:
        total_video_views = videos_data.get('total_views', 0)
        st.markdown(f'''<div class="page-overview-card">
            <h2>{format_number(total_video_views)}</h2>
            <p>🎬 Total Video Views</p>
        </div>''', unsafe_allow_html=True)

    with col5:
        st.markdown(f'''<div class="page-overview-card">
            <h2>{format_number(api_total_reactions)}</h2>
            <p>❤️ Total Reactions (API)</p>
        </div>''', unsafe_allow_html=True)

    with col6:
        st.markdown(f'''<div class="page-overview-card">
            <h2>{format_number(api_total_comments)}</h2>
            <p>💬 Total Comments (API)</p>
        </div>''', unsafe_allow_html=True)

    with col7:
        st.markdown(f'''<div class="page-overview-card">
            <h2>{format_number(api_total_shares)}</h2>
            <p>🔄 Total Shares (API)</p>
        </div>''', unsafe_allow_html=True)

    if api_post_count > 0:
        st.caption(f"📊 API data from {api_post_count} recent posts")

    st.markdown("---")

    # Check if we have data
    if df is None or df.empty:
        st.warning("No data available. Please add CSV exports to the 'exports' folder or run api_fetcher.py.")
        return

    # Show data source info
    st.sidebar.success(f"📊 Loaded {len(df):,} posts from CSV")

    # Sidebar filters
    st.sidebar.markdown("## 🎛️ Filters")

    today = datetime.now().date()
    min_date = df['date'].min()
    max_date = df['date'].max()

    time_periods = {
        'All Time': (min_date, max_date),
        'Today': (today, today),
        'Yesterday': (today - timedelta(days=1), today - timedelta(days=1)),
        'Last 7 Days': (today - timedelta(days=7), today),
        'Last 14 Days': (today - timedelta(days=14), today),
        'Last 30 Days': (today - timedelta(days=30), today),
        'Last 60 Days': (today - timedelta(days=60), today),
        'Last 90 Days': (today - timedelta(days=90), today),
        'Custom': None
    }

    selected_period = st.sidebar.selectbox("📅 Time Period", list(time_periods.keys()))

    if selected_period == 'Custom':
        date_range = st.sidebar.date_input("Custom Date Range", value=(min_date, max_date))
        if len(date_range) == 2:
            start_date, end_date = date_range
        else:
            start_date, end_date = min_date, max_date
    else:
        start_date, end_date = time_periods[selected_period]
        start_date = max(start_date, min_date)
        end_date = min(end_date, max_date)

    # Post type filter
    post_types = ['All'] + sorted(df['post_type_clean'].unique().tolist())
    selected_type = st.sidebar.selectbox("Post Type", post_types)

    # Apply filters
    filtered_df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
    if selected_type != 'All':
        filtered_df = filtered_df[filtered_df['post_type_clean'] == selected_type]

    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Showing:** {len(filtered_df):,} posts")
    st.sidebar.markdown(f"**Period:** {start_date} to {end_date}")

    # Data last updated
    fetched_at = posts_data.get('fetched_at', 'Unknown')
    if fetched_at != 'Unknown':
        fetched_dt = datetime.fromisoformat(fetched_at)
        st.sidebar.markdown(f"**Updated:** {fetched_dt.strftime('%Y-%m-%d %H:%M')}")

    # ===== MAIN KPIs =====
    st.markdown("### 📈 Performance Metrics")

    total_posts = len(filtered_df)
    total_engagement = filtered_df['engagement'].sum()
    total_reactions = filtered_df['reactions'].sum()
    total_comments = filtered_df['comments'].sum()
    total_shares = filtered_df['shares'].sum()
    avg_engagement = filtered_df['engagement'].mean() if total_posts > 0 else 0

    # Get Views and Reach from CSV if available
    total_views = filtered_df['views'].sum() if 'views' in filtered_df.columns else 0
    total_reach = filtered_df['reach'].sum() if 'reach' in filtered_df.columns else 0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'''<div class="post-type-card">
            <p class="subtitle">📊 Total Posts</p>
            <h3>{total_posts:,}</h3>
        </div>''', unsafe_allow_html=True)
    with col2:
        st.markdown(f'''<div class="post-type-card">
            <p class="subtitle">👁️ Total Views</p>
            <h3>{format_number(total_views)}</h3>
        </div>''', unsafe_allow_html=True)
    with col3:
        st.markdown(f'''<div class="post-type-card">
            <p class="subtitle">📣 Total Reach</p>
            <h3>{format_number(total_reach)}</h3>
        </div>''', unsafe_allow_html=True)
    with col4:
        st.markdown(f'''<div class="post-type-card">
            <p class="subtitle">💬 Total Engagement</p>
            <h3>{format_number(total_engagement)}</h3>
        </div>''', unsafe_allow_html=True)

    col5, col6, col7, col8 = st.columns(4)
    with col5:
        st.markdown(f'''<div class="post-type-card">
            <p class="subtitle">❤️ Total Reactions</p>
            <h3>{format_number(total_reactions)}</h3>
        </div>''', unsafe_allow_html=True)
    with col6:
        st.markdown(f'''<div class="post-type-card">
            <p class="subtitle">💭 Total Comments</p>
            <h3>{format_number(total_comments)}</h3>
        </div>''', unsafe_allow_html=True)
    with col7:
        st.markdown(f'''<div class="post-type-card">
            <p class="subtitle">🔄 Total Shares</p>
            <h3>{format_number(total_shares)}</h3>
        </div>''', unsafe_allow_html=True)
    with col8:
        st.markdown(f'''<div class="post-type-card">
            <p class="subtitle">📈 Avg Engagement</p>
            <h3>{format_number(avg_engagement)}</h3>
        </div>''', unsafe_allow_html=True)

    st.markdown("---")

    # ===== REACTION BREAKDOWN (only if API data available) =====
    # Check if we have reaction breakdown data (from API)
    has_reaction_data = 'like' in filtered_df.columns and filtered_df['like'].sum() > 0
    if has_reaction_data:
        posts_with_reactions = filtered_df[filtered_df['like'] > 0]

        # Get date range of posts with reaction data
        if 'date' in posts_with_reactions.columns and len(posts_with_reactions) > 0:
            reaction_dates = pd.to_datetime(posts_with_reactions['date'])
            reaction_min_date = reaction_dates.min().strftime('%b %d, %Y')
            reaction_max_date = reaction_dates.max().strftime('%b %d, %Y')
            reaction_post_count = len(posts_with_reactions)
            date_range_text = f"📅 Data from **{reaction_min_date}** to **{reaction_max_date}** ({reaction_post_count} posts with reaction data)"
        else:
            date_range_text = ""

        st.markdown("### 😊 Reaction Breakdown")
        if date_range_text:
            st.markdown(date_range_text)

        total_like = posts_with_reactions['like'].sum()
        total_love = posts_with_reactions['love'].sum()
        total_haha = posts_with_reactions['haha'].sum()
        total_wow = posts_with_reactions['wow'].sum()
        total_sad = posts_with_reactions['sad'].sum()
        total_angry = posts_with_reactions['angry'].sum()
        total_all_reactions = total_like + total_love + total_haha + total_wow + total_sad + total_angry

        col1, col2 = st.columns(2)

        with col1:
            # Reaction counts
            reaction_df = pd.DataFrame({
                'Reaction': ['👍 Like', '❤️ Love', '😆 Haha', '😮 Wow', '😢 Sad', '😠 Angry'],
                'Count': [total_like, total_love, total_haha, total_wow, total_sad, total_angry]
            })

            fig = px.pie(
                reaction_df,
                values='Count',
                names='Reaction',
                title=f'Reaction Distribution (Total: {format_number(total_all_reactions)})',
                color_discrete_sequence=['#4267B2', '#F02849', '#F7B928', '#F7B928', '#F7B928', '#E9573F'],
                hole=0.4
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Reaction bar chart
            fig = px.bar(
                reaction_df,
                x='Reaction',
                y='Count',
                title='Reactions by Type',
                color='Reaction',
                color_discrete_sequence=['#4267B2', '#F02849', '#F7B928', '#F7B928', '#F7B928', '#E9573F']
            )
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        st.markdown("---")

    # Note: Reaction breakdown is only available when API data is loaded

    # Charts row 1
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📊 Engagement by Post Type")
        type_stats = filtered_df.groupby('post_type_clean').agg({
            'engagement': 'sum',
            'reactions': 'sum',
            'comments': 'sum',
            'post_id': 'count'
        }).rename(columns={'post_id': 'posts'}).reset_index()

        fig = px.bar(
            type_stats,
            x='post_type_clean',
            y=['reactions', 'comments', 'engagement'],
            title='Reactions, Comments & Engagement by Post Type',
            barmode='group',
            color_discrete_sequence=['#4361EE', '#06D6A0', '#EC4899']
        )
        fig.update_layout(xaxis_title='Post Type', yaxis_title='Count', height=400)
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
        agg_dict = {
            'engagement': 'sum',
            'reactions': 'sum',
            'comments': 'sum'
        }
        # Add views and reach if available
        if 'views' in filtered_df.columns:
            agg_dict['views'] = 'sum'
        if 'reach' in filtered_df.columns:
            agg_dict['reach'] = 'sum'

        daily_stats = filtered_df.groupby('date').agg(agg_dict).reset_index()

        fig = go.Figure()
        # Add Views line (primary - most important)
        if 'views' in daily_stats.columns:
            fig.add_trace(go.Scatter(
                x=daily_stats['date'], y=daily_stats['views'],
                name='Views', line=dict(color='#10B981', width=2),
                fill='tozeroy', fillcolor='rgba(16, 185, 129, 0.1)'
            ))
        # Add Reach line
        if 'reach' in daily_stats.columns:
            fig.add_trace(go.Scatter(
                x=daily_stats['date'], y=daily_stats['reach'],
                name='Reach', line=dict(color='#F59E0B', width=2)
            ))
        # Add Engagement line
        fig.add_trace(go.Scatter(
            x=daily_stats['date'], y=daily_stats['engagement'],
            name='Engagement', line=dict(color='#4361EE', width=2)
        ))
        fig.update_layout(title='Daily Views, Reach & Engagement', height=400, hovermode='x unified')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### 📆 Monthly Engagement")
        monthly_stats = filtered_df.groupby('month').agg({
            'engagement': 'sum',
            'post_id': 'count'
        }).rename(columns={'post_id': 'posts'}).reset_index()

        fig = px.bar(
            monthly_stats,
            x='month',
            y='engagement',
            title='Monthly Engagement',
            color_discrete_sequence=['#4361EE']
        )
        fig.update_layout(xaxis_title='Month', yaxis_title='Total Engagement', height=400)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ===== TOP VIDEOS SECTION (NEW!) =====
    st.markdown("### 🎬 Top 10 Videos by Views")

    videos = videos_data.get('videos', [])
    if videos:
        videos_df = pd.DataFrame(videos)
        videos_df = videos_df.sort_values('views', ascending=False).head(10)

        # Format for display (API returns 'description' not 'title')
        display_videos = videos_df[['description', 'views', 'length', 'created_time', 'permalink_url']].copy()
        display_videos.columns = ['Title', 'Views', 'Duration (sec)', 'Created', 'Link']
        display_videos['Title'] = display_videos['Title'].fillna('Untitled').str[:50]
        display_videos['Views'] = display_videos['Views'].apply(lambda x: f"{int(x):,}")
        display_videos['Created'] = pd.to_datetime(display_videos['Created']).dt.strftime('%Y-%m-%d')

        # Fix relative URLs - add Facebook base URL
        display_videos['Link'] = display_videos['Link'].apply(
            lambda x: f"https://www.facebook.com{x}" if x and x.startswith('/') else x
        )

        st.dataframe(
            display_videos,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Link": st.column_config.LinkColumn("Link", display_text="View →")
            }
        )
    else:
        st.info("No video data available.")

    st.markdown("---")

    # Best posting times
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📆 Best Posting Days")
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_stats = filtered_df.groupby('day_of_week').agg({
            'engagement': ['count', 'sum', 'mean'],
            'reactions': 'mean',
            'comments': 'mean'
        })
        day_stats.columns = ['Posts', 'Total Engagement', 'Avg Engagement', 'Avg Reactions', 'Avg Comments']
        day_stats = day_stats.reindex(day_order).reset_index()

        for col in ['Posts', 'Total Engagement', 'Avg Engagement', 'Avg Reactions', 'Avg Comments']:
            day_stats[col] = day_stats[col].fillna(0).astype(int)

        best_day = day_stats.loc[day_stats['Avg Engagement'].idxmax(), 'day_of_week']

        st.dataframe(
            day_stats.style.highlight_max(subset=['Avg Engagement'], color=get_highlight_color()),
            use_container_width=True, hide_index=True
        )
        st.success(f"⭐ Best day: **{best_day}**")

    with col2:
        st.markdown("### ⏰ Best Posting Times")
        slot_order = ['Morning (6AM-12PM)', 'Afternoon (12PM-6PM)', 'Evening (6PM-10PM)', 'Night (10PM-6AM)']
        slot_stats = filtered_df.groupby('time_slot').agg({
            'engagement': ['count', 'sum', 'mean'],
            'reactions': 'mean',
            'comments': 'mean'
        })
        slot_stats.columns = ['Posts', 'Total Engagement', 'Avg Engagement', 'Avg Reactions', 'Avg Comments']
        slot_stats = slot_stats.reindex(slot_order).reset_index()

        for col in ['Posts', 'Total Engagement', 'Avg Engagement', 'Avg Reactions', 'Avg Comments']:
            slot_stats[col] = slot_stats[col].fillna(0).astype(int)

        best_slot = slot_stats.loc[slot_stats['Avg Engagement'].idxmax(), 'time_slot']

        st.dataframe(
            slot_stats.style.highlight_max(subset=['Avg Engagement'], color=get_highlight_color()),
            use_container_width=True, hide_index=True
        )
        st.success(f"⭐ Best time: **{best_slot}**")

    st.markdown("---")

    # Top Posts
    st.markdown("### 🏆 Top 15 Performing Posts")

    # Use permalink (from CSV) or permalink_url (from API)
    link_col = 'permalink' if 'permalink' in filtered_df.columns else 'permalink_url'

    top_posts = filtered_df.nlargest(15, 'engagement')[
        ['date', 'post_type_clean', 'message', 'reactions', 'comments', 'shares', 'engagement', link_col]
    ].copy()
    top_posts['message'] = top_posts['message'].fillna('').str[:80]
    top_posts.columns = ['Date', 'Type', 'Message', 'Reactions', 'Comments', 'Shares', 'Engagement', 'Link']

    for col in ['Reactions', 'Comments', 'Shares', 'Engagement']:
        top_posts[col] = top_posts[col].apply(lambda x: f"{int(x):,}")

    st.dataframe(
        top_posts,
        use_container_width=True,
        hide_index=True,
        column_config={"Link": st.column_config.LinkColumn("Link", display_text="View →")}
    )

    st.markdown("---")

    # All Posts Table
    st.markdown("### 📋 All Posts")

    all_posts = filtered_df.sort_values('date', ascending=False)[
        ['date', 'post_type_clean', 'message', 'reactions', 'comments', 'shares', 'engagement', link_col]
    ].copy()
    all_posts['message'] = all_posts['message'].fillna('').str[:60]
    all_posts.columns = ['Date', 'Type', 'Message', 'Reactions', 'Comments', 'Shares', 'Engagement', 'Link']

    st.dataframe(
        all_posts,
        use_container_width=True,
        height=600,
        column_config={"Link": st.column_config.LinkColumn("Link", display_text="View →")}
    )

    # Footer
    st.markdown("---")
    st.markdown(
        f"<p class='footer-text'>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M')} • Data from Facebook Graph API</p>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
