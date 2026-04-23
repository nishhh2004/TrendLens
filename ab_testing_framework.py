import sqlite3
import pandas as pd
from scipy import stats

def run_ab_test(conn):
    print("Loading data for A/B Testing...")
    # We can pull directly from the original video_stats table
    df = pd.read_sql_query("SELECT * FROM video_stats", conn)
    
    if df.empty:
        print("Error: No data found in database.")
        return

    print("\n--- A/B Test: Title Length vs. Engagement ---")
    print("Hypothesis: Do shorter titles drive higher Like-to-View ratios?")
    
    # Create the variable: Title Length
    df['title_length'] = df['title'].astype(str).apply(len)
    
    # Split into Group A and Group B
    # 50 characters is generally where titles start getting cut off on mobile
    group_a = df[df['title_length'] < 50]
    group_b = df[df['title_length'] >= 50]
    
    # The metric we are testing
    metric = 'like_to_view_pct'
    
    # Drop rows where the metric might be missing/zero due to disabled likes
    data_a = group_a[metric].dropna()
    data_b = group_b[metric].dropna()
    
    # Calculate Averages
    mean_a = data_a.mean()
    mean_b = data_b.mean()
    
    print(f"\nGroup A (Short Titles - Under 50 chars):")
    print(f"  - Videos: {len(data_a)}")
    print(f"  - Average Engagement Rate: {round(mean_a, 2)}%")
    
    print(f"\nGroup B (Long Titles - 50+ chars):")
    print(f"  - Videos: {len(data_b)}")
    print(f"  - Average Engagement Rate: {round(mean_b, 2)}%")
    
    # --- The Statistical Test (Independent T-Test) ---
    # This tells us if the difference is real, or just random luck.
    t_stat, p_value = stats.ttest_ind(data_a, data_b, equal_var=False)
    
    print("\n--- Statistical Results ---")
    print(f"T-Statistic: {round(t_stat, 3)}")
    print(f"P-Value: {round(p_value, 4)}")
    
    # Standard threshold for statistical significance is 0.05
    if p_value < 0.05:
        print("\nCONCLUSION: We have a Statistically Significant winner!")
        if mean_a > mean_b:
            print("Actionable Insight: Short titles definitively drive higher engagement. Optimize future content for brevity.")
        else:
            print("Actionable Insight: Long titles definitively drive higher engagement. Use descriptive hooks.")
    else:
        print("\nCONCLUSION: No statistical significance.")
        print("Actionable Insight: The difference in engagement is likely due to random chance. Title length does not strictly dictate engagement rates in this dataset.")

def main():
    conn = sqlite3.connect('youtube_data.db')
    try:
        run_ab_test(conn)
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()