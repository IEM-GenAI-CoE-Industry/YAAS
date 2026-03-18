from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"

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
