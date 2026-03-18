# from googleapiclient.discovery import build
# from googleapiclient.http import MediaFileUpload
# from google.oauth2.credentials import Credentials
# import datetime

# # Step 1: Define YouTube API scopes
# SCOPES = [
#     "https://www.googleapis.com/auth/youtube.upload",
#     "https://www.googleapis.com/auth/youtube.readonly"
# ]

# # Step 2: Simulate AI agent that generates metadata for the video
# def get_video_metadata(video_path: str):
#     current_time = datetime.datetime.utcnow()
#     scheduled_time = (current_time + datetime.timedelta(minutes=1)).isoformat("T") + "Z"  

#     title = "🎬 AI-Generated: How to Automate YouTube with Python"
#     description = (
#         "This video was uploaded by an AI Publishing Agent.\n"
#         "It automatically generated this title, description, and scheduled the video!"
#     )
#     tags = ["AI", "Python", "YouTube API", "Automation", "Agent"]
#     privacy = "private"  

#     return {
#         "title": title,
#         "description": description,
#         "tags": tags,
#         "privacy": privacy,
#         "scheduled_time": scheduled_time
#     }

# # Step 3: Upload video to YouTube with AI-generated metadata
# def upload_video_ai():
#     creds = Credentials.from_authorized_user_file("token.json", SCOPES)
#     service = build("youtube", "v3", credentials=creds)

#     video_path = "sample-video.mp4"
#     metadata = get_video_metadata(video_path)

#     # AI Decision Display
#     print("\n🤖 AI-Powered Metadata Decision:")
#     print("Title: ", metadata["title"])
#     print("Description: ", metadata["description"])
#     print("Tags: ", metadata["tags"])
#     print("Privacy: ", metadata["privacy"])
#     print("Scheduled Time (UTC): ", metadata["scheduled_time"])
#     print("\n📦 Uploading video to YouTube...")

#     body = {
#         "snippet": {
#             "title": metadata["title"],
#             "description": metadata["description"],
#             "tags": metadata["tags"],
#             "categoryId": "22"  # 'People & Blogs'
#         },
#         "status": {
#             "privacyStatus": metadata["privacy"],
#             "publishAt": metadata["scheduled_time"] if metadata["privacy"] == "private" else None,
#             "selfDeclaredMadeForKids": False,
#         }
#     }

#     media = MediaFileUpload(video_path, chunksize=-1, resumable=True)

#     try:
#         request = service.videos().insert(
#             part="snippet,status",
#             body=body,
#             media_body=media
#         )
#         response = request.execute()
#         print("\n✅ Video uploaded successfully!")
#         print("📺 Video ID:", response["id"])

#         # Simulated Dashboard
#         print("\n📊 Scheduled Video Dashboard:")
#         print("="*60)
#         print(f"{'Title':<30} | {'Scheduled Time':<20} | {'Status'}")
#         print("-"*60)
#         print(f"{metadata['title'][:28]:<30} | {metadata['scheduled_time']:<20} | ✅ Scheduled")

#     except Exception as e:
#         print("❌ Error during upload:", e)

# # Entry point
# if __name__ == "__main__":
#     upload_video_ai()


# import os
# import cv2
# import datetime
# import numpy as np
# import pickle
# from tensorflow.keras.models import load_model
# from tensorflow.keras.preprocessing.image import load_img, img_to_array
# from tensorflow.keras.preprocessing.sequence import pad_sequences
# from google.oauth2.credentials import Credentials
# from googleapiclient.discovery import build
# from googleapiclient.http import MediaFileUpload

# # === CONFIGURATION ===
# SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
# VIDEO_PATH = "sample-video.mp4"
# MODEL_PATH = "model.keras"
# TOKENIZER_PATH = "tokenizer.pkl"
# FEATURE_EXTRACTOR_PATH = "feature_extractor.keras"
# IMG_SIZE = 224
# MAX_CAPTION_LENGTH = 34
# FRAME_INTERVAL = 30  # Extract 1 frame every 30 frames (~1 sec for 30fps)

# # === Load Models & Tokenizer ===
# caption_model = load_model(MODEL_PATH)
# feature_extractor = load_model(FEATURE_EXTRACTOR_PATH)
# with open(TOKENIZER_PATH, "rb") as f:
#     tokenizer = pickle.load(f)

# # === Utility: Generate caption for image ===
# def generate_caption_from_image(image_array):
#     img = image_array / 255.0
#     img = np.expand_dims(img, axis=0)
#     features = feature_extractor.predict(img, verbose=0)

#     in_text = "startseq"
#     for _ in range(MAX_CAPTION_LENGTH):
#         sequence = tokenizer.texts_to_sequences([in_text])[0]
#         sequence = pad_sequences([sequence], maxlen=MAX_CAPTION_LENGTH)
#         yhat = caption_model.predict([features, sequence], verbose=0)
#         yhat_index = np.argmax(yhat)
#         word = tokenizer.index_word.get(yhat_index)
#         if word is None or word == "endseq":
#             break
#         in_text += " " + word
#     return in_text.replace("startseq", "").strip()

# # === Extract meaningful frames from video ===
# def extract_captions(video_path):
#     cap = cv2.VideoCapture(video_path)
#     frame_count = 0
#     captions = []

#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             break
#         if frame_count % FRAME_INTERVAL == 0:
#             frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#             img = cv2.resize(frame_rgb, (IMG_SIZE, IMG_SIZE))
#             caption = generate_caption_from_image(img)
#             captions.append(caption)
#         frame_count += 1
#     cap.release()
#     return captions

# # === Generate YouTube metadata using AI ===
# def generate_youtube_metadata_from_captions(captions):
#     joined = ". ".join(captions)
#     top_captions = list(dict.fromkeys(captions))[:5]

#     title = f"AI-Generated Highlights: {top_captions[0].capitalize() if top_captions else 'A Journey'}"
#     description = (
#         "🤖 This video was analyzed using an AI-powered image captioning model.\n\n"
#         "📌 Top Moments:\n" + "\n".join(f"- {cap}" for cap in top_captions) + 
#         "\n\nGenerated by an autonomous AI publishing agent."
#     )
#     tags = list({word for cap in top_captions for word in cap.split() if len(word) > 3})
#     return title, description, tags

# # === Upload to YouTube ===
# def upload_to_youtube(title, description, tags, video_path):
#     creds = Credentials.from_authorized_user_file("token.json", SCOPES)
#     service = build("youtube", "v3", credentials=creds)

#     scheduled_time = (datetime.datetime.utcnow() + datetime.timedelta(minutes=1)).isoformat("T") + "Z"
#     body = {
#         "snippet": {
#             "title": title,
#             "description": description,
#             "tags": tags,
#             "categoryId": "22"
#         },
#         "status": {
#             "privacyStatus": "private",
#             "publishAt": scheduled_time,
#             "selfDeclaredMadeForKids": False,
#         }
#     }

#     media = MediaFileUpload(video_path, chunksize=-1, resumable=True)

#     request = service.videos().insert(
#         part="snippet,status",
#         body=body,
#         media_body=media
#     )
#     response = request.execute()
#     print(f"\n✅ Uploaded successfully! Video ID: {response['id']}")
#     print(f"⏰ Scheduled for: {scheduled_time}")
#     print(f"📌 Title: {title}\n📝 Description:\n{description}\n🏷️ Tags: {tags}")

# # === MAIN ===
# if __name__ == "__main__":
#     print("🔍 Extracting captions from video...")
#     captions = extract_captions(VIDEO_PATH)

#     print("🧠 Generating YouTube metadata...")
#     title, description, tags = generate_youtube_metadata_from_captions(captions)

#     print("📤 Uploading to YouTube...")
#     upload_to_youtube(title, description, tags, VIDEO_PATH)

import os
import datetime
import whisper
import tempfile
import numpy as np
import cv2
from moviepy.editor import VideoFileClip
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from transformers import pipeline
from PIL import Image
import torch
from transformers import BlipProcessor, BlipForConditionalGeneration

# Paths and settings
VIDEO_PATH = "sample1.mp4"
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
TOKEN_PATH = "token.json"

# Load models
whisper_model = whisper.load_model("base")
generator = pipeline("text-generation", model="gpt2", do_sample=True, temperature=0.7, top_k=50, top_p=0.95, repetition_penalty=1.2)
device = "cuda" if torch.cuda.is_available() else "cpu"
blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").to(device)

# ---------- Step 1: Audio Transcription ----------
def extract_audio_transcription(video_path):
    try:
        clip = VideoFileClip(video_path)
        if clip.audio is None:
            return None
        temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
        clip.audio.write_audiofile(temp_audio, verbose=False, logger=None)
        result = whisper_model.transcribe(temp_audio)
        os.remove(temp_audio)
        return result["text"]
    except Exception as e:
        print("⚠️ Audio analysis failed:", e)
        return None

# ---------- Step 2: Visual Frame Captions ----------
def extract_visual_captions(video_path, max_frames=3):
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    interval = max(1, total_frames // max_frames)
    captions = []

    for i in range(0, total_frames, interval):
        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ret, frame = cap.read()
        if not ret:
            break
        temp_path = f"temp_frame_{i}.jpg"
        cv2.imwrite(temp_path, frame)
        caption = generate_blip_caption(temp_path)
        captions.append(caption)
        os.remove(temp_path)
        if len(captions) >= max_frames:
            break

    cap.release()
    return captions

def generate_blip_caption(image_path):
    image = Image.open(image_path).convert("RGB")
    inputs = blip_processor(image, return_tensors="pt").to(device)
    out = blip_model.generate(**inputs)
    caption = blip_processor.decode(out[0], skip_special_tokens=True)
    return caption

# ---------- Step 3: GPT Metadata Generation ----------
def generate_metadata(text):
    prompt = (
        "You are a YouTube content expert. Based on the following content, "
        "generate a catchy video title, a 2–3 line engaging description, and 5 relevant tags.\n\n"
        f"CONTENT:\n{text.strip()}\n\n"
        "Return in this format:\n"
        "Title: <title here>\n"
        "Description: <description here>\n"
        "Tags: <tag1>, <tag2>, <tag3>, <tag4>, <tag5>"
    )

    result = generator(prompt, max_new_tokens=150)[0]['generated_text']
    print("\n[LLM Raw Output]\n", result)

    title, desc, tags = "Untitled Video", "No description provided.", ["AI", "Generated", "Video"]
    try:
        for line in result.splitlines():
            if line.lower().startswith("title:"):
                title = line.split(":", 1)[1].strip()
            elif line.lower().startswith("description:"):
                desc = line.split(":", 1)[1].strip()
            elif line.lower().startswith("tags:"):
                tags = [t.strip() for t in line.split(":", 1)[1].split(",") if t.strip()]
    except Exception as e:
        print("⚠️ Metadata parse error:", e)

    return title, desc, tags

# ---------- Step 4: Upload to YouTube ----------
def upload_video(title, description, tags):
    if not title.strip():
        raise ValueError("❌ Invalid or empty video title.")

    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    service = build("youtube", "v3", credentials=creds)

    scheduled_time = (datetime.datetime.utcnow() + datetime.timedelta(minutes=1)).isoformat("T") + "Z"
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "22"
        },
        "status": {
            "privacyStatus": "private",
            "publishAt": scheduled_time,
            "selfDeclaredMadeForKids": False
        }
    }

    media = MediaFileUpload(VIDEO_PATH, chunksize=-1, resumable=True)
    request = service.videos().insert(part="snippet,status", body=body, media_body=media)
    response = request.execute()

    print("✅ Uploaded to YouTube!")
    print("🎬 Title:", title)
    print("📝 Description:", description)
    print("🏷️ Tags:", tags)
    print("📺 Video ID:", response['id'])
    print("🕒 Scheduled for:", scheduled_time)

# ---------- Main Workflow ----------
def main():
    print("🔍 Checking audio...")
    transcript = extract_audio_transcription(VIDEO_PATH)

    print("🖼️ Extracting visual captions...")
    visual_captions = extract_visual_captions(VIDEO_PATH)

    content = ""
    if transcript:
        print("✅ Audio transcription found.")
        content += transcript + "\n\n"
    else:
        print("🔇 No audio found.")

    content += "\n".join(visual_captions)

    print("🧠 Generating metadata...")
    title, desc, tags = generate_metadata(content)

    print("\n🚀 Uploading to YouTube...")
    upload_video(title, desc, tags)

if __name__ == "__main__":
    main()
