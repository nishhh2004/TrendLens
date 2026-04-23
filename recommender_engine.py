import sqlite3
import pandas as pd
from collections import Counter
import re
from datetime import datetime

STOP_WORDS = set(['the', 'a', 'to', 'and', 'in', 'of', 'for', 'with', 'on', 'how', 'is', 'my', 'i', 'this', 'you', 'what', 'why'])

def generate_trending_recommendations(conn):
    print("Loading data for the Time-Aware Recommender...")
    
    try:
        df = pd.read_sql_query("SELECT * FROM final_video_analytics", conn)
    except Exception:
        print("Error: Could not find 'final_video_analytics'.")
        return

    if df.empty:
        print("Error: No data found.")
        return

    print("\nApplying Time-Decay to find CURRENT trends...")
    
    # 1. Convert published_at to actual datetime objects
    # Handle cases where the date string might be empty or malformed
    df['published_at'] = pd.to_datetime(df['published_at'], errors='coerce')
    df = df.dropna(subset=['published_at'])
    
    # 2. Find the "Current Date" of our dataset (the newest video)
    most_recent_date = df['published_at'].max()
    
    # 3. Calculate how many days old each video is relative to the newest video
    df['days_old'] = (most_recent_date - df['published_at']).dt.days
    
    # 4. Calculate the TRENDING SCORE (Time Decay Formula)
    # We divide the viral coefficient by a time factor. 
    # Videos older than 30 days start losing their influence quickly.
    df['trending_score'] = df['viral_coefficient'] / (1 + (df['days_old'] / 30))
    
    print("Isolating the top 15% of TRENDING videos for the coming week...")
    # Isolate top 15% based on the NEW trending score, not the all-time score
    threshold = df['trending_score'].quantile(0.85)
    trending_performers = df[df['trending_score'] >= threshold].copy()
    
    # 5. Analyze Format (Title Length)
    trending_performers['title_length'] = trending_performers['title'].astype(str).apply(len)
    optimal_length = trending_performers['title_length'].median()
    
    # 6. Analyze Hooks (Questions vs Statements)
    trending_performers['is_question'] = trending_performers['title'].str.contains(r'\?', na=False)
    question_ratio = trending_performers['is_question'].mean() * 100
    best_hook = "Question Hook (?)" if question_ratio > 50 else "Statement Hook (No ?)"
    
    # 7. Analyze Sentiment (Emotional Tone)
    avg_sentiment = trending_performers['sentiment_score'].mean()
    if avg_sentiment > 0.2:
        tone = "Highly Positive / Inspirational"
    elif avg_sentiment < -0.1:
        tone = "Negative / Controversial / Venting"
    else:
        tone = "Neutral / Educational / Relatable"
        
    # 8. Analyze Topics (Keyword Extraction)
    all_titles = " ".join(trending_performers['title'].astype(str)).lower()
    words = re.findall(r'\b[a-z]{3,}\b', all_titles)
    meaningful_words = [w for w in words if w not in STOP_WORDS]
    top_keywords = [word for word, count in Counter(meaningful_words).most_common(3)]

    # ==========================================
    # PRINT THE PRESCRIPTIVE STRATEGY REPORT
    # ==========================================
    print("\n" + "="*60)
    print("🚀 OPTIMAL CONTENT STRATEGY FOR THE COMING WEEK 🚀")
    print("="*60)
    print(f"Based on time-decay modeling of current data (Newest video: {most_recent_date.date()}),")
    print("here is the exact blueprint optimized for immediate algorithmic trends:\n")
    
    # Safety check if we don't have enough words
    if len(top_keywords) >= 3:
        print(f"📌 1. TRENDING TOPICS: The algorithm is currently favoring these themes:")
        print(f"      -> '{top_keywords[0].upper()}', '{top_keywords[1].upper()}', or '{top_keywords[2].upper()}'")
    else:
        print(f"📌 1. TRENDING TOPICS: Insufficient text data to extract topics.")
    
    print(f"\n📌 2. OPTIMAL FORMAT: Target a title length of ~{int(optimal_length)} characters.")
    if optimal_length < 50:
        print("      (Audiences are currently responding best to short, punchy titles).")
    else:
        print("      (Audiences are currently engaging with long, highly descriptive titles).")
        
    print(f"\n📌 3. WINNING HOOK: Use a {best_hook}.")
    if best_hook == "Question Hook (?)":
        print("      (Questions are actively driving higher comment-to-view ratios right now).")
    else:
        print("      (Direct statements are currently outperforming questions).")
        
    print(f"\n📌 4. REQUIRED TONE: Keep the emotional delivery {tone}.")
    
    print("\n" + "="*60)
    print("End of Report.")

def main():
    conn = sqlite3.connect('youtube_data.db')
    try:
        generate_trending_recommendations(conn)
    finally:
        conn.close()

if __name__ == "__main__":
    main()