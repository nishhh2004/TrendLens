import os
import time
import pandas as pd
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
from sqlalchemy import create_engine

# ============================================================
# CONFIG & SECURE SETUP
# ============================================================
load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")

if not API_KEY:
    raise ValueError("API Key not found. Please set YOUTUBE_API_KEY in your .env file.")

# Database connection
DB_URL = os.getenv("DATABASE_URL", "sqlite:///youtube_data.db")
engine = create_engine(DB_URL)

SEARCH_TOPICS = [
    "daily vlog", "mental health", "study with me", "cooking recipes",
    "fitness workout", "travel tips", "personal finance", "coding tutorial",
    "motivation", "true crime", "book review", "gaming highlights",
    "fashion haul", "productivity tips", "relationship advice",
    "startup journey", "photography tips", "language learning",
    "meditation", "news commentary"
]

CHANNELS_TARGET    = 50  
VIDEOS_PER_CHANNEL = 4   
COMMENTS_PER_VIDEO = 30  

youtube = build("youtube", "v3", developerKey=API_KEY)

# ============================================================
# Step 1 — Auto-discover channels (Now with Pagination)
# ============================================================
def discover_channels(target=CHANNELS_TARGET):
    channel_ids = set()

    for topic in SEARCH_TOPICS:
        if len(channel_ids) >= target:
            break

        print(f"  Searching topic: '{topic}'")
        next_page_token = None
        
        while len(channel_ids) < target:
            try:
                response = youtube.search().list(
                    part="snippet",
                    q=topic,
                    type="video",
                    maxResults=50, # Maximize results per API call
                    relevanceLanguage="en",
                    order="viewCount",
                    pageToken=next_page_token
                ).execute()

                for item in response.get("items", []):
                    channel_ids.add(item["snippet"]["channelId"])
                    if len(channel_ids) >= target:
                        break

                next_page_token = response.get("nextPageToken")
                if not next_page_token:
                    break # Exhausted results for this topic

            except HttpError as e:
                print(f"  API Error on topic '{topic}': {e}")
                break # Move to next topic on error
            
            time.sleep(0.5)

    return list(channel_ids)[:target]

# ============================================================
# Step 2 — Get top video IDs from a channel
# ============================================================
def get_video_ids(channel_id, max_results=VIDEOS_PER_CHANNEL):
    try:
        response = youtube.search().list(
            part="id",
            channelId=channel_id,
            maxResults=max_results,
            order="viewCount",  
            type="video"
        ).execute()

        return [item["id"]["videoId"] for item in response.get("items", [])]

    except HttpError as e:
        print(f"    API Error getting videos for {channel_id}: {e}")
        return []

# ============================================================
# Step 3 — Get video stats 
# ============================================================
def get_video_stats(video_ids):
    if not video_ids:
        return []

    try:
        response = youtube.videos().list(
            part="snippet,statistics",
            id=",".join(video_ids)
        ).execute()

        stats = []
        for item in response.get("items", []):
            s  = item.get("statistics", {})
            sn = item.get("snippet", {})
            
            # Engineered Proxies for Virality
            views = int(s.get("viewCount", 0))
            likes = int(s.get("likeCount", 0))
            comments = int(s.get("commentCount", 0))
            
            like_ratio = round((likes / views) * 100, 4) if views > 0 else 0
            comment_ratio = round((comments / views) * 100, 4) if views > 0 else 0

            stats.append({
                "video_id"         : item["id"],
                "channel_id"       : sn.get("channelId"),
                "channel_name"     : sn.get("channelTitle"),
                "title"            : sn.get("title"),
                "published_at"     : sn.get("publishedAt", "")[:10],  
                "views"            : views,
                "likes"            : likes,
                "comment_count"    : comments,
                "like_to_view_pct" : like_ratio,
                "comm_to_view_pct" : comment_ratio
            })
        return stats

    except HttpError as e:
        print(f"    API Error getting stats: {e}")
        return []

# ============================================================
# Step 4 — Get comments
# ============================================================
def get_comments(video_id, channel_name, max_results=COMMENTS_PER_VIDEO):
    comments = []
    try:
        response = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=max_results,
            order="relevance"
        ).execute()

        for item in response.get("items", []):
            c = item["snippet"]["topLevelComment"]["snippet"]
            comments.append({
                "video_id"     : video_id,
                "channel_name" : channel_name,
                "comment"      : c.get("textDisplay", ""),
                "comment_likes": int(c.get("likeCount", 0)),
            })

    except HttpError as e:
        # 403 usually means comments are disabled.
        if e.resp.status == 403:
            pass 
        else:
            print(f"    API Error getting comments for {video_id}: {e}")

    return comments

# ============================================================
# Main Data Pipeline
# ============================================================
def main():
    all_videos   = []
    all_comments = []

    print("Discovering channels from mixed niches...")
    channel_ids = discover_channels()
    print(f"Found {len(channel_ids)} unique channels\n")

    try:
        for i, channel_id in enumerate(channel_ids, 1):
            print(f"[{i}/{len(channel_ids)}] Processing channel: {channel_id}")

            video_ids = get_video_ids(channel_id)
            if not video_ids:
                continue

            stats = get_video_stats(video_ids)
            all_videos.extend(stats)

            for video in stats:
                comments = get_comments(video["video_id"], video["channel_name"])
                all_comments.extend(comments)

            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\nProcess interrupted by user. Saving data collected so far...")

    # ============================================================
    # Save — Pushing Directly to SQL Database
    # ============================================================
    print("\nPushing data to database...")
    
    if all_videos:
        df_videos = pd.DataFrame(all_videos).drop_duplicates("video_id")
        # Push to DB, append if table exists
        df_videos.to_sql("video_stats", con=engine, if_exists="append", index=False)
        print(f"  Saved {len(df_videos)} videos to DB.")

    if all_comments:
        df_comments = pd.DataFrame(all_comments).drop_duplicates()
        df_comments.to_sql("comments", con=engine, if_exists="append", index=False)
        print(f"  Saved {len(df_comments)} comments to DB.")

    print("\nData extraction complete!")

if __name__ == "__main__":
    main()