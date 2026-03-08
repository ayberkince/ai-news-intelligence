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
    get_summary_history,
    get_summary_topics
)
from app.ai_summary import summarize_articles
from app.pipeline import run_ingestion_pipeline
from app.database import init_db, save_summary,save_report
from app.topic_analytics import analyze_topic_trends
from app.report_builder import build_intelligence_report
from app.queries import get_report_history # NEW import

# Initialize database schema
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
    st.subheader("📊 Analytics Settings")
    analytics_window = st.slider("Summaries to analyze for trends", 5, 100, 20)
    
    st.subheader("📜 History Settings")
    history_limit = st.slider("History entries to show", 5, 50, 10)

    if st.button("🔄 Refresh Dashboard", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# --- DATA PREPARATION (The "Engine" Layer) ---
# We fetch everything first so the Intelligence Report can be built correctly.
total_articles = load_metrics()
latest_articles = load_latest_articles(article_limit, selected_source)
top_sources_data = load_top_sources()
latest_summary_row = load_latest_summary()
raw_topic_data = get_summary_topics(limit=analytics_window)

# Process topics for the report builder
top_topics = []
if raw_topic_data:
    trend_df = analyze_topic_trends(raw_topic_data)
    if not trend_df.empty:
        top_topics = trend_df.values.tolist()

# BUILD THE STRUCTURED REPORT
report = build_intelligence_report(
    total_articles=total_articles,
    displayed_articles=len(latest_articles),
    top_sources=top_sources_data,
    latest_summary_row=latest_summary_row,
    top_topics=top_topics
)

# --- MAIN PAGE LAYOUT ---
st.title("📰 AI News Intelligence Dashboard")
st.write("Synthetic market monitoring and structured intelligence reporting.")

# 1. Top Level Metrics
m_col1, m_col2, m_col3 = st.columns(3)
m_col1.metric("Database Volume", f"{total_articles} Articles")
m_col2.metric("Active Sources", len(load_sources()) - 1)
m_col3.metric("Analysis Scope", f"{len(latest_articles)} Headlines")

# 2. THE INTELLIGENCE REPORT (Day 14 Strategic Layer)
st.markdown("---")
with st.container():
    st.subheader("📋 Intelligence Report")
    
    if report["report_timestamp"]:
        st.caption(f"Report Generated At: {report['report_timestamp']}")
    

    rep_left, rep_right = st.columns([2, 1])
    
    # ... end of rep_right column ...

    # Add the Save Button inside the container, spanning the full width
    if st.button("💾 Save Report Snapshot", use_container_width=True):
        save_report(report)
        st.success("Report snapshot successfully archived!")
        time.sleep(1)
        st.rerun()

    st.markdown("---")

    with rep_left:
        st.markdown("#### ⚡ What Matters Now")
        st.info(report["what_matters_now"])
        
        st.markdown("#### 🤖 Executive Summary")
        if report["summary_text"]:
            st.write(report["summary_text"])
            if report["summary_topics"]:
                tags = " ".join([f"`{t}`" for t in report["summary_topics"]])
                st.markdown(tags)
        else:
            st.warning("No summary available for this specific filter. Please generate a new summary below.")

    with rep_right:
        st.markdown("#### 📊 Theme Dominance")
        if report["top_topics"]:
            for topic, count in report["top_topics"][:5]:
                st.write(f"**{topic}** ({count})")
                # Visual bar scaled to 10 as a 'high' frequency
                st.progress(min(count / 10, 1.0))
        else:
            st.caption("No trend data available.")

        st.markdown("#### 📡 Top Sources")
        if report["top_sources"]:
            for src, count in report["top_sources"][:3]:
                st.caption(f"**{src}**: {count} articles")

st.markdown("---")

# 3. Action Layer: AI Synthesis
st.subheader("🧠 Intelligence Generation")
if st.button("✨ Generate New AI Summary", use_container_width=True):
    if latest_articles:
        with st.spinner("Gemini is synthesizing new intelligence..."):
            ai_output = summarize_articles(latest_articles)
            
            # Extract data from the JSON output
            new_summary = ai_output.get("summary", "No summary generated.")
            topics_list = ai_output.get("topics", ["General"])
            topics_string = ", ".join(topics_list)
            
            save_summary(
                summary_text=new_summary, 
                topics=topics_string, 
                source_filter=selected_source, 
                article_limit=article_limit
            )
            st.success("New intelligence saved to database!")
            st.cache_data.clear()
            st.rerun()

# 4. Detailed Data Layers (Tabs for cleaner UI)
tab1, tab2, tab3, tab4 = st.tabs(["🔥 Latest Articles", "📈 Market Trends", "🕰️ History","💾 Saved Reports"])

with tab1:
    col_news, col_src_list = st.columns([2, 1])
    with col_news:
        if not latest_articles:
            st.info("No articles match the current filter.")
        for title, source, published_at in latest_articles:
            st.markdown(f"**[{source}]** {title}")
            st.caption(published_at)
    with col_src_list:
        st.write("**Top Source Distribution**")
        for src, count in top_sources_data:
            st.write(f"- {src}: {count}")

with tab2:
    st.write("### Quantitative Theme Analytics")
    if raw_topic_data:
        trend_df = analyze_topic_trends(raw_topic_data)
        if not trend_df.empty:
            st.bar_chart(trend_df.set_index("Topic"))
            st.dataframe(trend_df, hide_index=True, use_container_width=True)
    else:
        st.info("Generate more summaries to see trend data.")

with tab3:
    st.write("### Intelligence Timeline")
    history = load_summary_history(history_limit)
    if history:
        for h_id, h_text, h_topics, h_filter, h_limit, h_at in history:
            with st.expander(f"📅 {h_at} | Filter: {h_filter}"):
                if h_topics:
                    st.markdown(" ".join([f"`{t.strip()}`" for t in h_topics.split(",")]))
                st.write(h_text)
                st.caption(f"Context: {h_limit} articles")
    else:
        st.info("No history found.")

with tab4:
    st.write("### 🗄️ Intelligence Report Archive")
    st.write("Review previous market snapshots and AI syntheses.")
    
    report_rows = get_report_history(limit=history_limit)
    
    if report_rows:
        for row in report_rows:
            (r_id, r_time, t_art, d_art, matters_now, sum_text, dom_topics, 
             top_srcs, s_filter, a_limit, created_at) = row
            
            preview = matters_now[:100] + "..." if matters_now else "No preview available"
            
            with st.expander(f"📑 Report: {created_at} | Context: {s_filter}"):
                st.markdown("#### ⚡ What Matters Now")
                st.info(matters_now)
                
                st.markdown("#### 🤖 Summary")
                st.write(sum_text)
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown("**Dominant Topics**")
                    if dom_topics:
                        for item in dom_topics.split(","):
                            st.write(f"- `{item.strip()}`")
                with col_b:
                    st.markdown("**Top Sources**")
                    if top_srcs:
                        for item in top_srcs.split(","):
                            st.write(f"- {item.strip()}")
                
                st.markdown("---")
                st.caption(f"Database ID: {r_id} | Total DB Articles: {t_art} | Analyzed: {d_art}")
    else:
        st.info("No reports saved yet. Click 'Save Report Snapshot' above to archive your first report.")