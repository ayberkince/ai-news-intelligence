import sys
import os
import streamlit as st
import time

# 1. Setup Path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 2. Consolidated Imports
from app.queries import (
    count_articles, 
    get_latest_articles, 
    get_top_sources, 
    get_all_sources, 
    get_latest_summary,
    get_summary_history
)
from app.ai_summary import summarize_articles
from app.pipeline import run_ingestion_pipeline
from app.database import init_db, save_summary
from app.queries import get_summary_topics
from app.topic_analytics import analyze_topic_trends

# Ensure the database schema is up to date (this handles the 'topics' column migration)
init_db()

st.set_page_config(page_title="AI News Intelligence", page_icon="📰", layout="wide")

# --- CACHED DATA LOADERS ---
@st.cache_data(ttl=300)
def load_metrics(): return count_articles()

@st.cache_data(ttl=300)
def load_sources(): return ["All"] + get_all_sources()

@st.cache_data(ttl=300)
def load_latest_articles(limit, source):
    return get_latest_articles(limit=limit, source_filter=source)

@st.cache_data(ttl=300)
def load_top_sources(): return get_top_sources(limit=5)

@st.cache_data(ttl=300)
def load_latest_summary(): return get_latest_summary()

@st.cache_data(ttl=60)
def load_summary_history(limit): return get_summary_history(limit=limit)

# --- SIDEBAR ---
with st.sidebar:
    st.header("🎛️ System Controls")
    
    if st.button("📥 Fetch New Articles", type="primary", use_container_width=True):
        with st.spinner("Running ETL Pipeline..."):
            result = run_ingestion_pipeline()
            st.success(f"Added {result['inserted_count']} new articles!")
            time.sleep(1)
            st.cache_data.clear()
            st.rerun()
            
    st.markdown("---")
    st.subheader("🔍 Analysis Filters")
    article_limit = st.slider("Articles to analyze", 3, 20, 5)
    selected_source = st.selectbox("Filter by source", load_sources())
    
    st.markdown("---")
    st.subheader("📜 History Settings")
    history_limit = st.slider("History entries to show", 5, 50, 10)
    
    st.markdown("---")
    st.subheader("📊 Analytics Settings")
    analytics_window = st.slider("Summaries to analyze for trends", 5, 100, 20)

    if st.button("🔄 Refresh Dashboard", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# --- MAIN PAGE ---
st.title("📰 AI News Intelligence Dashboard")
st.write("Interactive AI-powered news monitoring and market sentiment tracking.")
st.markdown("---")

# Metrics
col1, col2 = st.columns(2)
with col1:
    st.metric("Total Stored Articles", load_metrics())
with col2:
    st.metric("Displayed Articles", len(load_latest_articles(article_limit, selected_source)))

st.markdown("---")

# News and Sources
col_news, col_sources = st.columns([2, 1])
with col_news:
    latest_articles = load_latest_articles(limit=article_limit, source=selected_source)
    st.subheader(f"🔥 Latest Articles ({selected_source})")
    if not latest_articles:
        st.info("No articles found.")
    for title, source, published_at in latest_articles:
        st.markdown(f"**{title}**")
        st.caption(f"{source} | {published_at}")

with col_sources:
    st.subheader("📈 Top Sources")
    for source, count in load_top_sources():
        st.write(f"- **{source}**: {count}")

st.markdown("---")

# --- AI SYNTHESIS LAYER ---
st.subheader("🧠 Executive AI Summary")

if st.button("✨ Generate New AI Summary", use_container_width=True):
    articles_to_summarize = load_latest_articles(limit=article_limit, source=selected_source)
    if articles_to_summarize:
        with st.spinner("AI is synthesizing market data..."):
            ai_output = summarize_articles(articles_to_summarize)
            
            # Defensive check: handle if AI returns a string instead of dict
            if isinstance(ai_output, dict):
                new_summary = ai_output.get("summary", "")
                topics_list = ai_output.get("topics", [])
                topics_string = ", ".join(topics_list)
            else:
                new_summary = ai_output
                topics_string = "General"
            
            save_summary(summary_text=new_summary, topics=topics_string, 
                         source_filter=selected_source, article_limit=article_limit)
            st.success("Analysis Complete!")
            st.cache_data.clear()
            st.rerun()

# Latest Summary Display
latest_summary_row = load_latest_summary()
if latest_summary_row:
    # Safely handle different row lengths
    summary_text = latest_summary_row[0]
    topics = latest_summary_row[1]
    created_at = latest_summary_row[4]
    
    st.info(f"**Current Intelligence** ({created_at})")
    if topics:
        topic_tags = " ".join([f"`{t.strip()}`" for t in topics.split(",")])
        st.markdown(topic_tags)
    st.write(summary_text)

# --- TREND ANALYTICS LAYER ---
st.markdown("---")
st.subheader("📊 Market Theme Analytics")
st.write("Quantitative frequency of AI-extracted topics over recent history.")

# 1. Fetch the data
raw_topic_data = get_summary_topics(limit=analytics_window)

# 2. Process the data
if raw_topic_data:
    trend_df = analyze_topic_trends(raw_topic_data)
    
    if not trend_df.empty:
        col_chart, col_data = st.columns([2, 1])
        
        with col_chart:
            # Streamlit natively handles Pandas DataFrames for charting!
            st.bar_chart(data=trend_df.set_index("Topic"), use_container_width=True)
            
        with col_data:
            st.dataframe(trend_df, use_container_width=True, hide_index=True)
    else:
        st.info("Not enough structured topic data to generate trends.")
else:
    st.info("No topic history available.")

# --- INTELLIGENCE TIMELINE ---
st.markdown("---")
st.subheader("🕰️ Intelligence Timeline")

history_rows = load_summary_history(limit=history_limit)
if history_rows:
    for row in history_rows:
        # s_id, text, topics, s_filter, s_limit, s_at
        h_id, h_text, h_topics, h_filter, h_limit, h_at = row
        preview = h_text[:100].replace("\n", " ") + "..."
        
        with st.expander(f"📅 {h_at} | {h_filter}"):
            if h_topics:
                st.markdown(" ".join([f"`{t.strip()}`" for t in h_topics.split(",")]))
            st.markdown(f"**Preview:** *{preview}*")
            st.markdown("---")
            st.write(h_text)
            st.caption(f"Context: {h_limit} articles | ID: {h_id}")
else:
    st.info("No historical summaries yet.")