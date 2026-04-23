import sqlite3
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score

def prepare_data(conn):
    print("Loading data from database...")
    # Load videos
    df_videos = pd.read_sql_query("SELECT * FROM video_stats", conn)
    
    # Load analyzed comments
    df_comments = pd.read_sql_query("SELECT video_id, relatability_tag, sentiment_score FROM comments_analyzed", conn)
    
    if df_videos.empty or df_comments.empty:
        raise ValueError("Database is missing data. Run previous modules first!")

    print("Aggregating NLP data to the video level...")
    # Calculate average sentiment per video
    avg_sentiment = df_comments.groupby('video_id')['sentiment_score'].mean().reset_index()
    
    # Calculate percentage of comments that are "Relatable"
    # Create a binary column first: 1 if Relatable, 0 if Neutral
    df_comments['is_relatable'] = df_comments['relatability_tag'].apply(lambda x: 1 if x == 'Relatable' else 0)
    relatability_pct = df_comments.groupby('video_id')['is_relatable'].mean().reset_index()
    relatability_pct.rename(columns={'is_relatable': 'relatability_ratio'}, inplace=True)

    # Merge everything together
    df_merged = pd.merge(df_videos, avg_sentiment, on='video_id', how='left')
    df_merged = pd.merge(df_merged, relatability_pct, on='video_id', how='left')
    
    # Fill any missing values with 0
    df_merged.fillna(0, inplace=True)
    return df_merged

def calculate_viral_coefficient(df):
    print("Calculating the custom Viral Coefficient...")
    # We weigh our proxy metrics to create a single target score (0 to 100+)
    # You can adjust these weights based on what you consider most important
    weight_likes = 0.3
    weight_comments = 0.3
    weight_relatability = 0.4 
    
    df['viral_coefficient'] = (
        (df['like_to_view_pct'] * weight_likes * 10) + 
        (df['comm_to_view_pct'] * weight_comments * 50) + 
        (df['relatability_ratio'] * weight_relatability * 100)
    )
    return df

def train_model(df):
    print("\n--- Training Virality Prediction Model ---")
    
    # Define our Features (X) and our Target (y)
    # We drop ID and text columns because the model needs numbers
    features = ['views', 'likes', 'comment_count', 'like_to_view_pct', 'comm_to_view_pct', 'sentiment_score', 'relatability_ratio']
    X = df[features]
    y = df['viral_coefficient']
    
    # Split data into training (80%) and testing (20%) sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Initialize and train the Random Forest
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Test the model
    predictions = model.predict(X_test)
    r2 = r2_score(y_test, predictions)
    
    print(f"Model R-squared score: {round(r2, 3)} (1.0 is perfect prediction)")
    
    # Show Feature Importance (What actually drives virality?)
    importances = model.feature_importances_
    feature_importance_df = pd.DataFrame({
        'Feature': features,
        'Importance': importances
    }).sort_values(by='Importance', ascending=False)
    
    print("\n--- What drives Virality? (Feature Importance) ---")
    print(feature_importance_df.to_string(index=False))
    
    return model, df

def main():
    conn = sqlite3.connect('youtube_data.db')
    
    try:
        # Pipeline
        df = prepare_data(conn)
        df = calculate_viral_coefficient(df)
        model, final_df = train_model(df)
        
        # Save the final dataset with viral coefficients back to the DB for the dashboard
        final_df.to_sql("final_video_analytics", conn, if_exists="replace", index=False)
        print("\nSaved final analytics to 'final_video_analytics' table.")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()