"""
Zero-cost Veo 3 access check.
Only calls models.list() — no generation, no billing.
"""
import os
from dotenv import load_dotenv
from google import genai

load_dotenv(".env")

key = os.environ.get("GEMINI_API_KEY")
if not key:
    print("ERROR: GEMINI_API_KEY not found in .env")
    exit(1)

print(f"Using key: {key[:8]}...{key[-4:]}\n")

client = genai.Client(api_key=key)

all_models = [m.name for m in client.models.list()]
veo_models = [m for m in all_models if "veo" in m.lower()]

TARGET = "models/veo-3.1-generate-preview"

print(f"Total accessible models: {len(all_models)}")
print(f"\nVeo models available on this key:")
if veo_models:
    for m in veo_models:
        tag = " ← TARGET ✅" if m == TARGET else ""
        print(f"  - {m}{tag}")
else:
    print("  ⚠️  No Veo models found — key may lack Veo 3 access")

if TARGET not in veo_models:
    print(f"\n❌ '{TARGET}' NOT accessible.")
    print("   → This key needs Veo 3 allowlist access from Google.")
    print("   → Apply here: https://aistudio.google.com/")
else:
    print(f"\n✅ '{TARGET}' is accessible. Key is ready for video generation.")
