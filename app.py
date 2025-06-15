from flask import Flask, render_template, request, redirect, url_for, send_file, flash, jsonify
from yt_dlp import YoutubeDL
from dotenv import load_dotenv
import os, re, glob, json, requests
from datetime import datetime

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'defaultsecret')

DOWNLOAD_FOLDER = "downloads"
HISTORY_FOLDER = "history"
HISTORY_FILE = os.path.join(HISTORY_FOLDER, "download_history.json")
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"

os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
os.makedirs(HISTORY_FOLDER, exist_ok=True)

def log_download(video_id, title, filename):
    entry = {
        "video_id": video_id,
        "title": title,
        "filename": filename,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    history = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            history = json.load(f)
    history.append(entry)
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def load_downloaded_video_ids():
    if not os.path.exists(HISTORY_FILE):
        return set()
    with open(HISTORY_FILE, "r") as f:
        history = json.load(f)
        return {entry["video_id"] for entry in history}

@app.route('/', methods=['GET', 'POST'])
def index():
    videos = []
    downloaded_ids = load_downloaded_video_ids()

    if request.method == 'POST':
        query = request.form.get('query', '').strip()
        if not query:
            flash("Please enter a search term.")
            return render_template("index.html", videos=[])

        if not YOUTUBE_API_KEY:
            flash("Missing YOUTUBE_API_KEY.")
            return render_template("index.html", videos=[])

        match = re.search(r"(?:v=|youtu\.be/)([\w-]{11})", query)
        if match:
            video_id = match.group(1)
            params = {'part': 'snippet,status', 'id': video_id, 'key': YOUTUBE_API_KEY}
            response = requests.get(YOUTUBE_VIDEO_URL, params=params)
            if response.status_code == 200:
                data = response.json()
                if data['items']:
                    video_data = data['items'][0]
                    license_type = video_data.get('status', {}).get('license', 'unknown')
                    if license_type != 'creativeCommon':
                        flash("Video is not Creative Commons licensed.")
                        return render_template("index.html", videos=[])
                    videos.append({
                        'title': video_data['snippet']['title'],
                        'thumbnail': video_data['snippet']['thumbnails']['medium']['url'],
                        'video_id': video_id,
                        'video_url': f"https://www.youtube.com/watch?v={video_id}",
                        'downloaded': video_id in downloaded_ids
                    })
            else:
                flash("YouTube API error while retrieving video info.")
        else:
            params = {
                'part': 'snippet',
                'q': query,
                'key': YOUTUBE_API_KEY,
                'type': 'video',
                'videoLicense': 'creativeCommon',
                'maxResults': 10
            }
            response = requests.get(YOUTUBE_SEARCH_URL, params=params)
            if response.status_code == 200:
                data = response.json()
                for item in data.get('items', []):
                    video_id = item['id']['videoId']
                    videos.append({
                        'video_id': video_id,
                        'title': item['snippet']['title'],
                        'thumbnail': item['snippet']['thumbnails']['medium']['url'],
                        'video_url': f"https://www.youtube.com/watch?v={video_id}",
                        'downloaded': video_id in downloaded_ids
                    })
            else:
                flash("YouTube search API failed.")

    return render_template("index.html", videos=videos)

@app.route('/start_download', methods=['POST'])
def start_download():
    data = request.get_json()
    video_id = data.get('video_id')
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    ydl_opts = {
        'format': 'best',
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
        'quiet': True
    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info)
            title = info.get("title", "Unknown Title")
        log_download(video_id, title, os.path.basename(filename))
        return jsonify(success=True, filename=os.path.basename(filename))
    except Exception as e:
        return jsonify(success=False, error=str(e))

@app.route('/download_file/<filename>')
def download_file(filename):
    path = os.path.join(DOWNLOAD_FOLDER, filename)
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    return "File not found", 404

if __name__ == "__main__":
    app.run(debug=True)
