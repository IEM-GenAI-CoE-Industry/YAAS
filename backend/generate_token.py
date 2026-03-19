"""
Re-generate token.json from downloaded client_secrets.json.
Run this once: python generate_token.py
"""
import json
import os
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
]

if not os.path.exists("client_secrets.json"):
    print("ERROR: client_secrets.json not found! Make sure you downloaded your OAuth credentials and saved them as client_secrets.json.")
    exit(1)

print("Opening browser for YouTube OAuth...")
print("Sign in with the Google account that owns the YouTube channel.\n")

try:
    flow = InstalledAppFlow.from_client_secrets_file('client_secrets.json', SCOPES)
    # Using port 8080. You MUST add http://localhost:8080/ to your Authorized Redirect URIs in Google Cloud Console!
    creds = flow.run_local_server(port=8080, access_type="offline", prompt="consent")
except Exception as e:
    print(f"\n❌ Error starting the OAuth flow:")
    print(str(e))
    exit(1)

token_data = {
    "token": creds.token,
    "refresh_token": creds.refresh_token,
    "token_uri": creds.token_uri,
    "client_id": creds.client_id,
    "client_secret": creds.client_secret,
    "scopes": list(creds.scopes) if creds.scopes else SCOPES,
    "universe_domain": "googleapis.com",
    "account": "",
    "expiry": creds.expiry.isoformat() if creds.expiry else None,
}

with open("token.json", "w") as f:
    json.dump(token_data, f, indent=4)

print("\n✅ token.json generated and saved successfully!")
print(f"   Refresh token: {creds.refresh_token[:20] if creds.refresh_token else 'None'}...")
print("\nYou can now use the Publish Agent in the YAAS pipeline.")
