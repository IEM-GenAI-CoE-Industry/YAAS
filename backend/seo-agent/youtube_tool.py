from googleapiclient.discovery import build
import os
from dotenv import load_dotenv

load_dotenv()

def fetch_competitor_data(keyword: str) -> str:
    api_key = os.getenv("youtube_api_key")
    if not api_key:
        return "Error: YouTube API key not found in .env"
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
        # Initial search to get video IDs
        search_request = youtube.search().list(
            q=keyword,
            part='snippet',
            type='video',
            maxResults=3,
            order='viewCount'
        )
        search_response = search_request.execute()
        video_ids = [item['id']['videoId'] for item in search_response.get('items', []) if 'id' in item and 'videoId' in item['id']]

        if not video_ids:
            return "No videos found for the keyword."

        # Fetch detailed video data including tags
        videos_request = youtube.videos().list(
            part='snippet',
            id=','.join(video_ids)
        )
        videos_response = videos_request.execute()
        videos = [
            {
                'title': item['snippet']['title'],
                'description': item['snippet']['description'],
                'tags': item['snippet'].get('tags', [])
            }
            for item in videos_response.get('items', [])
        ]
        return videos
    except Exception as e:
        return f"Error fetching YouTube data: {str(e)}"

# Tool is simply a reference to the function
youtube_tool = fetch_competitor_data

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')

    results = youtube_tool("python tutorials")

    if isinstance(results, str):
        print(results)
    else:
        for idx, video in enumerate(results):
            print(f"Video {idx+1}:")
            print("Title:", video['title'])
            print("Description:", video['description'])
            print("Tags:", video['tags'])
            print("-"*50)
