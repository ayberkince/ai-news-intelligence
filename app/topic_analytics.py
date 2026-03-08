import pandas as pd
from collections import Counter
from typing import List, Tuple

def analyze_topic_trends(topic_rows: List[Tuple[str, str]]) -> pd.DataFrame:
    """Aggregates topic frequencies, filters out errors, and returns a DataFrame."""
    counter = Counter()

    # 1. THE FILTER: Define tags we NEVER want on our analytics chart
    EXCLUDED_TAGS = {
        "api error", 
        "system error", 
        "error", 
        "fallback", 
        "general news"
    }

    for topics_text, _ in topic_rows:
        if not topics_text:
            continue

        # Split the string by commas and clean up extra spaces
        raw_topics = [t.strip() for t in topics_text.split(",") if t.strip()]
        
        # 2. APPLY FILTER: Keep it only if it's not in our excluded list
        valid_topics = [
            t.title() for t in raw_topics 
            if t.lower() not in EXCLUDED_TAGS
        ]
        
        counter.update(valid_topics)

    # Convert the Counter object directly into a DataFrame
    if not counter:
        return pd.DataFrame(columns=["Topic", "Frequency"])
        
    df = pd.DataFrame(counter.most_common(), columns=["Topic", "Frequency"])
    return df