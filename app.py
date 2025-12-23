import os
import json
from fastapi import FastAPI, Request, UploadFile, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from tinydb import TinyDB, Query
from datetime import datetime
import pytz

import google_auth_oauthlib.flow
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from utils.youtube_uploader import upload_video, get_credentials
from utils.gemini_chain import generate_metadata


CLIENT_SECRET_FILE = "client_secrets.json"
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/userinfo.email",
    "openid"
]

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

app = FastAPI(title="YouTube Publishing Agent")

templates = Jinja2Templates(directory="templates")
db = TinyDB("db.json")


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/login")
def login():
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        scopes=SCOPES
    )
    flow.redirect_uri = "http://localhost:8000/oauth2callback"

    auth_url, _ = flow.authorization_url(
        access_type="offline",
        prompt="consent",
        include_granted_scopes="false"
    )

    return RedirectResponse(auth_url)


@app.get("/oauth2callback")
def oauth2callback(request: Request):
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        scopes=SCOPES
    )
    flow.redirect_uri = "http://localhost:8000/oauth2callback"
    flow.fetch_token(authorization_response=str(request.url))

    creds = flow.credentials

    request_adapter = google_requests.Request()
    id_info = id_token.verify_oauth2_token(
        creds.id_token,
        request_adapter
    )

    email = id_info.get("email", "unknown")

    db.upsert(
        {
            "email": email,
            "refresh_token": creds.refresh_token
        },
        Query().email == email
    )

    response = RedirectResponse("/upload")
    response.set_cookie("email", email, httponly=True)
    return response


@app.get("/upload", response_class=HTMLResponse)
def upload_page(request: Request):
    email = request.cookies.get("email")
    if not email:
        return RedirectResponse("/")

    return templates.TemplateResponse(
        "upload.html",
        {"request": request, "email": email}
    )


@app.post("/upload")
async def handle_upload(
    request: Request,
    video: UploadFile,
    summary: str = Form(...),
    scheduled_time: str = Form(...)
):
    email = request.cookies.get("email")
    if not email:
        return RedirectResponse("/")

    naive_dt = datetime.strptime(scheduled_time, "%Y-%m-%dT%H:%M")
    ist = pytz.timezone("Asia/Kolkata")
    ist_dt = ist.localize(naive_dt)
    utc_dt = ist_dt.astimezone(pytz.utc)
    rfc3339_time = utc_dt.isoformat().replace("+00:00", "Z")

    if utc_dt <= datetime.utcnow().replace(tzinfo=pytz.utc):
        return HTMLResponse("❌ Scheduled time must be in the future")

    os.makedirs("uploads", exist_ok=True)
    filepath = f"uploads/{video.filename}"

    with open(filepath, "wb") as f:
        f.write(await video.read())

    user = db.get(Query().email == email)
    with open(CLIENT_SECRET_FILE) as f:
        secrets = json.load(f)["web"]

    creds = get_credentials(
        refresh_token=user["refresh_token"],
        client_id=secrets["client_id"],
        client_secret=secrets["client_secret"],
        scopes=SCOPES
    )

    metadata = generate_metadata(summary)
    metadata["scheduled_time"] = rfc3339_time
    metadata["privacy"] = "private"

    response = upload_video(filepath, creds, metadata)

    if not response or "id" not in response:
        return HTMLResponse("❌ Upload failed")

    return HTMLResponse(f"""
        <h3>✅ Video Scheduled Successfully</h3>
        <p><b>IST:</b> {ist_dt.strftime("%Y-%m-%d %I:%M %p")}</p>
        <p><b>UTC:</b> {rfc3339_time}</p>
        <a href="https://youtube.com/watch?v={response['id']}" target="_blank">
            Watch on YouTube
        </a>
    """)
