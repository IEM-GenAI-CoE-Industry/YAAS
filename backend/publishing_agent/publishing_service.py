from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

from util.constants import YOUTUBE_UPLOAD_SCOPE

def upload_video(video_path: str, creds, metadata: dict) -> dict:
    """
    Uploads a video to YouTube using provided OAuth credentials and metadata.
    """

    service = build("youtube", "v3", credentials=creds)

    body = {
        "snippet": {
            "title": metadata["title"],
            "description": metadata["description"],
            "tags": metadata.get("tags", []),
            "categoryId": "22",  # People & Blogs
        },
        "status": {
            "privacyStatus": metadata.get("privacy", "private"),
            "publishAt": metadata.get("scheduled_time"),
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(
        video_path,
        chunksize=-1,
        resumable=True
    )

    request = service.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media,
    )

    response = request.execute()
    return response

def run_publishing_agent(global_state: dict) -> dict:
    """
    Entry point for the Publishing Agent.
    Reads 'seo_metadata' and 'video_path' from global state.
    """
    metadata = global_state.get("seo_metadata", {})
    video_path = global_state.get("video_path")
    
    if not metadata or not video_path:
        raise ValueError("Publishing Agent requires 'seo_metadata' and 'video_path' in global state.")
        
    try:
        from google.oauth2.credentials import Credentials
        creds = Credentials.from_authorized_user_file(
            "token.json",
            scopes=[
                "https://www.googleapis.com/auth/youtube.upload",
                "https://www.googleapis.com/auth/youtube.readonly",
            ],
        )
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                from google.auth.transport.requests import Request as GoogleRequest
                creds.refresh(GoogleRequest())
            else:
                raise Exception("Token invalid or expired with no refresh token")
        global_state["oauth_required"] = False
    except Exception as e:
        print(f"Auth error (token.json missing or invalid): {e}")
        global_state["oauth_required"] = True
        return global_state
        
    print(f"Uploading video {video_path} to YouTube...")
    response = upload_video(video_path, creds, metadata)
    
    global_state["publish_response"] = response
    return global_state
