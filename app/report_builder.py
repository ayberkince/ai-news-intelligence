# app/report_builder.py

def generate_what_matters_now(top_topics, top_sources):
    """Rule-based synthetic insight generator."""
    messages = []

    if top_topics:
        # Assuming top_topics is a list of tuples [(topic, count), ...]
        dominant_topic, dominant_count = top_topics[0]
        messages.append(
            f"The most dominant recent theme is '{dominant_topic}' appearing {dominant_count} times."
        )

    if top_sources:
        # Assuming top_sources is a list of tuples [(source, count), ...]
        dominant_source, source_count = top_sources[0]
        messages.append(
            f"The most active source is '{dominant_source}' with {source_count} articles."
        )

    if not messages:
        return "Not enough data yet to identify dominant themes."

    return " ".join(messages)

def build_intelligence_report(
    total_articles,
    displayed_articles,
    top_sources,
    latest_summary_row,
    top_topics
):
    """Combines different platform intelligence pieces into one structured object."""
    summary_text = ""
    summary_topics = []
    summary_timestamp = None
    source_filter = None
    article_limit = None

    # Unpack the database row if it exists
    if latest_summary_row:
        # Database order: summary_text, topics, source_filter, article_limit, created_at
        summary_text, topics, source_filter, article_limit, created_at = latest_summary_row
        summary_timestamp = created_at
        if topics:
            summary_topics = [t.strip() for t in topics.split(",") if t.strip()]

    what_matters_now = generate_what_matters_now(top_topics, top_sources)

    report = {
        "report_timestamp": summary_timestamp,
        "total_articles": total_articles,
        "displayed_articles": displayed_articles,
        "top_sources": top_sources,
        "summary_text": summary_text,
        "summary_topics": summary_topics,
        "top_topics": top_topics,
        "source_filter": source_filter,
        "article_limit": article_limit,
        "what_matters_now": what_matters_now,
    }

    return report