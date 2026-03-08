import sys
import os
import streamlit as st
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.queries import count_articles, get_latest_articles, get_top_sources, get_all_sources
from app.ai_summary import summarize_articles
from app.pipeline import run_ingestion_pipeline

st.set_page_config(page_title="AI News Intelligence", page_icon="📰", layout="wide")

# --- CACHED DATA LOADERS ---
@st.cache_data(ttl=300)
def load_metrics() -> int:
    return count_articles()

@st.cache_data(ttl=300)
def load_sources() -> list[str]:
    return ["All"] + get_all_sources()

@st.cache_data(ttl=300)
def load_latest_articles(limit: int, source: str):
    return get_latest_articles(limit=limit, source_filter=source)

@st.cache_data(ttl=300)
def load_top_sources():
    return get_top_sources(limit=5)

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("🎛️ Dashboard Controls")
    
    if st.button("📥 Fetch New Articles", type="primary", use_container_width=True):
        with st.spinner("Running ETL Pipeline..."):
            result = run_ingestion_pipeline()
            st.success(f"Added {result['inserted_count']} new articles!")
            time.sleep(2) # Give the user time to read the success message
            st.cache_data.clear() # CRITICAL: Wipe old memory
            st.rerun() # Refresh page with new DB data
            
    st.markdown("---")
    
    article_limit = st.slider("Number of articles to analyze", min_value=3, max_value=20, value=5)
    available_sources = load_sources()
    selected_source = st.selectbox("Filter by source", available_sources)
    
    st.markdown("---")
    generate_summary = st.button("🧠 Generate AI Summary", use_container_width=True)
    
    st.markdown("---")
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# --- MAIN PAGE LAYOUT ---
st.title("📰 AI News Intelligence Dashboard")
st.write("Interactive AI-powered news monitoring system.")
st.markdown("---")

total_articles = load_metrics()
latest_articles = load_latest_articles(limit=article_limit, source=selected_source)
top_sources = load_top_sources()

col1, col2 = st.columns(2)
with col1:
    st.metric("Total Stored Articles", total_articles)
with col2:
    st.metric("Displayed Articles", len(latest_articles))

st.markdown("---")
col_news, col_sources = st.columns([2, 1])

with col_news:
    st.subheader(f"🔥 Latest Articles ({selected_source})")
    if not latest_articles:
        st.info("No articles found for the selected filter.")
    for title, source, published_at in latest_articles:
        st.markdown(f"**{title}**")
        st.caption(f"{source} | {published_at}")

with col_sources:
    st.subheader("📈 Top Sources Overview")
    for source, article_count in top_sources:
        st.write(f"- **{source}**: {article_count}")

st.markdown("---")

# --- AI SYNTHESIS LAYER ---
st.subheader("🧠 Executive AI Summary")
if generate_summary:
    if latest_articles:
        with st.spinner(f"Analyzing {len(latest_articles)} articles from {selected_source}..."):
            summary = summarize_articles(latest_articles)
            st.success("Analysis Complete")
            st.write(summary)
    else:
        st.warning("No articles available for summarization.")
else:
    st.info("Click 'Generate AI Summary' in the sidebar to synthesize the visible articles.")