import sqlite3
import pandas as pd
from textblob import TextBlob

# ============================================================
# CONFIG: The "Problem Awareness" Dictionary
# ============================================================
# These are the phrases that indicate high relatability and connection.
# You can add more slang or niche-specific terms here later!
RELATABLE_KEYWORDS = [
    "relatable", "literally me", "feel seen", "struggle", 
    "finally someone", "exactly", "i feel this", "so true",
    "story of my life", "going through this", "needed to hear this",
    "spot on", "makes me feel less alone", "describe me"
]

def analyze_relatability(text):
    if not isinstance(text, str):
        return pd.Series(["Neutral", 0.0])

    text_lower = text.lower()
    
    # 1. Calculate general emotional sentiment (-1.0 to 1.0)
    polarity = TextBlob(text).sentiment.polarity
    
    # 2. Check for Problem Awareness / Relatability triggers
    is_relatable = any(keyword in text_lower for keyword in RELATABLE_KEYWORDS)
    
    # We tag it "Relatable" if it hits our keywords.
    tag = "Relatable" if is_relatable else "Neutral"
    
    return pd.Series([tag, round(polarity, 3)])

def main():
    print("Connecting to database...")
    # Connect directly to the SQLite file you just generated
    conn = sqlite3.connect('youtube_data.db')
    
    # Load the raw comments into a Pandas DataFrame
    print("Loading comments...")
    df = pd.read_sql_query("SELECT * FROM comments", conn)
    
    if df.empty:
        print("No comments found in the database. Run the collector script first!")
        return

    print(f"Analyzing {len(df)} comments for relatability. This might take a moment...")
    
    # Apply our NLP function to create two new columns
    df[['relatability_tag', 'sentiment_score']] = df['comment'].apply(analyze_relatability)
    
    # Count the results
    relatable_count = len(df[df['relatability_tag'] == 'Relatable'])
    print(f"\nAnalysis Complete!")
    print(f"Found {relatable_count} highly relatable comments.")
    
    # Save the results into a brand NEW table so we don't ruin the raw data
    df.to_sql("comments_analyzed", conn, if_exists="replace", index=False)
    print("Saved analyzed data to the 'comments_analyzed' table in your database.")
    
    conn.close()

if __name__ == "__main__":
    main()