from flask import Flask, render_template, request, redirect, url_for, send_file, flash, jsonify
from yt_dlp import YoutubeDL
from dotenv import load_dotenv
import os, re, json, requests, logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

# Load environment variables
load_dotenv(dotenv_path=".secrets/.env")

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "defaultsecret")

# Logging setup
if not os.path.exists("logs"):
    os.mkdir("logs")
log_file = os.path.join("logs", "app.log")
file_handler = RotatingFileHandler(log_file, maxBytes=10240, backupCount=5)
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)

# Config
DOWNLOAD_FOLDER = "downloads"
HISTORY_FOLDER = "history"
DATA_FOLDER = "data"
PLAYLIST_FILE = os.path.join(DATA_FOLDER, "playlists.json")
HISTORY_FILE = os.path.join(HISTORY_FOLDER, "download_history.json")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"

# Ensure folders and playlist file exist
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
os.makedirs(HISTORY_FOLDER, exist_ok=True)
os.makedirs(DATA_FOLDER, exist_ok=True)

if not os.path.exists(PLAYLIST_FILE):
    with open(PLAYLIST_FILE, "w") as f:
        json.dump([], f)

# Helpers
def log_download(video_id, title, filename, thumbnail_url=None):
    entry = {
        "video_id": video_id,
        "title": title,
        "filename": filename,
        "thumbnail": thumbnail_url or f"https://img.youtube.com/vi/{video_id}/0.jpg",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    history = load_download_history()
    history.insert(0, entry)
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def load_downloaded_video_ids():
    if not os.path.exists(HISTORY_FILE):
        return set()
    with open(HISTORY_FILE, "r") as f:
        history = json.load(f)
        return {entry["video_id"] for entry in history}

def load_download_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return []

# Routes
@app.route("/", methods=["GET", "POST"])
def index():
    videos = []
    downloaded_ids = load_downloaded_video_ids()

    if request.method == "POST":
        query = request.form.get("query", "").strip()

        if not query:
            flash("Please enter a search term.")
            return render_template("index.html", videos=[])

        if not YOUTUBE_API_KEY:
            flash("Missing YOUTUBE_API_KEY.")
            return render_template("index.html", videos=[])

        try:
            match = re.search(r"(?:v=|youtu\\.be/)([\\w-]{11})", query)
            if match:
                video_id = match.group(1)
                params = {"part": "snippet,status", "id": video_id, "key": YOUTUBE_API_KEY}
                response = requests.get(YOUTUBE_VIDEO_URL, params=params)
                response.raise_for_status()
                data = response.json()
                if data["items"]:
                    video_data = data["items"][0]
                    license_type = video_data.get("status", {}).get("license", "unknown")
                    if license_type != "creativeCommon":
                        flash("Video is not Creative Commons licensed.")
                        return render_template("index.html", videos=[])
                    videos.append({
                        "title": video_data["snippet"]["title"],
                        "thumbnail": video_data["snippet"]["thumbnails"]["medium"]["url"],
                        "video_id": video_id,
                        "video_url": f"https://www.youtube.com/watch?v={video_id}",
                        "downloaded": video_id in downloaded_ids
                    })
            else:
                params = {
                    "part": "snippet",
                    "q": query,
                    "key": YOUTUBE_API_KEY,
                    "type": "video",
                    "videoLicense": "creativeCommon",
                    "maxResults": 10
                }
                response = requests.get(YOUTUBE_SEARCH_URL, params=params)
                response.raise_for_status()
                data = response.json()
                for item in data.get("items", []):
                    video_id = item.get("id", {}).get("videoId")
                    if not video_id:
                        app.logger.warning(f"Skipped item without videoId: {item}")
                        continue
                    videos.append({
                        "video_id": video_id,
                        "title": item["snippet"]["title"],
                        "thumbnail": item["snippet"]["thumbnails"]["medium"]["url"],
                        "video_url": f"https://www.youtube.com/watch?v={video_id}",
                        "downloaded": video_id in downloaded_ids
                    })
        except Exception as e:
            app.logger.error("Error during search", exc_info=e)
            flash("An error occurred while processing your request.")

    return render_template("index.html", videos=videos)

@app.route("/start_download", methods=["POST"])
def start_download():
    data = request.get_json()
    video_id = data.get("video_id")
    video_url = f"https://www.youtube.com/watch?v={video_id}"

    ydl_opts = {
        "format": "best",
        "outtmpl": os.path.join(DOWNLOAD_FOLDER, "%(title)s.%(ext)s"),
        "quiet": True
    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info)
            title = info.get("title", "Unknown Title")
            thumbnail = info.get("thumbnail")
        log_download(video_id, title, os.path.basename(filename), thumbnail)
        return jsonify(success=True, filename=os.path.basename(filename))
    except Exception as e:
        app.logger.error("Download failed", exc_info=e)
        return jsonify(success=False, error=str(e))

@app.route("/download_file/<filename>")
def download_file(filename):
    path = os.path.join(DOWNLOAD_FOLDER, filename)
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    return "File not found", 404

@app.route("/history")
def history():
    history_data = load_download_history()
    query = request.args.get("q", "").lower()
    if query:
        history_data = [v for v in history_data if query in v["title"].lower()]

    page = int(request.args.get("page", 1))
    per_page = 5
    total = len(history_data)
    paginated = history_data[(page - 1) * per_page: page * per_page]
    total_pages = (total + per_page - 1) // per_page

    all_playlists = []
    video_to_playlists = {}

    try:
        with open(PLAYLIST_FILE, "r") as f:
            all_playlists = json.load(f)
        for pl in all_playlists:
            for v in pl["videos"]:
                video_to_playlists.setdefault(v["video_id"], set()).add(pl["name"])
    except Exception as e:
        app.logger.warning("Could not load playlists for history dropdown", exc_info=e)

    return render_template(
        "history.html",
        history=paginated,
        page=page,
        total_pages=total_pages,
        all_playlists=all_playlists,
        video_to_playlists=video_to_playlists
    )


@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/delete_video/<video_id>", methods=["POST"])
def delete_video(video_id):
    history = load_download_history()
    updated = [v for v in history if v["video_id"] != video_id]
    with open(HISTORY_FILE, "w") as f:
        json.dump(updated, f, indent=2)
    return redirect(url_for("history"))

@app.route("/check_playlists")
def check_playlists():
    if os.path.exists(PLAYLIST_FILE):
        with open(PLAYLIST_FILE, "r") as f:
            playlists = json.load(f)
        return jsonify(exists=bool(playlists))
    return jsonify(exists=False)

@app.route("/create_playlist")
def create_playlist():
    return render_template("create_playlist.html")

@app.route("/save_playlist", methods=["POST"])
def save_playlist():
    playlist_name = request.form.get("playlist_name", "").strip()

    if not playlist_name:
        flash("Playlist name is required.")
        return redirect(url_for("create_playlist"))

    playlist = {
        "name": playlist_name,
        "videos": []
    }

    existing = []
    try:
        with open(PLAYLIST_FILE, "r") as f:
            content = f.read().strip()
            if content:
                existing = json.loads(content)
    except Exception as e:
        app.logger.warning("Failed to load playlists during save", exc_info=e)

    existing.append(playlist)

    with open(PLAYLIST_FILE, "w") as f:
        json.dump(existing, f, indent=2)

    app.logger.info(f"New playlist created: {playlist_name}")
    flash(f"Playlist '{playlist_name}' created successfully.")
    return redirect(url_for("playlists"))

@app.route("/assign_to_playlist", methods=["POST"])
def assign_to_playlist():
    video_id = request.form.get("video_id")
    playlist_name = request.form.get("playlist_name")

    history = load_download_history()
    video = next((v for v in history if v["video_id"] == video_id), None)

    if not video:
        flash("Video not found in history.")
        return redirect(url_for("history"))

    try:
        with open(PLAYLIST_FILE, "r") as f:
            playlists = json.load(f)
        for p in playlists:
            if p["name"] == playlist_name:
                if video not in p["videos"]:
                    p["videos"].append(video)
                break
        with open(PLAYLIST_FILE, "w") as f:
            json.dump(playlists, f, indent=2)
        flash(f"Video added to playlist '{playlist_name}'.")
    except Exception as e:
        app.logger.error("Failed to assign video to playlist", exc_info=e)
        flash("Error assigning video to playlist.")

    return redirect(url_for("history"))

@app.route("/playlists")
def playlists():
    playlists = []
    try:
        if os.path.exists(PLAYLIST_FILE):
            with open(PLAYLIST_FILE, "r") as f:
                content = f.read().strip()
                if content:
                    playlists = json.loads(content)
                else:
                    app.logger.warning("playlists.json is empty.")
        return render_template("playlists.html", playlists=playlists)
    except json.JSONDecodeError as e:
        app.logger.error("Invalid JSON in playlists.json", exc_info=e)
        flash("There was an error loading your playlists. Please recreate them.")
        return render_template("playlists.html", playlists=[])
    except Exception as e:
        app.logger.error("Unexpected error loading playlists", exc_info=e)
        flash("Unexpected error loading playlists.")
        return render_template("playlists.html", playlists=[])

@app.route("/log_js_error", methods=["POST"])
def log_js_error():
    try:
        error_data = request.get_json()
        app.logger.error("JS Error: %s (line %s, col %s) — %s\n%s",
            error_data.get("source", "unknown"),
            error_data.get("line", "?"),
            error_data.get("column", "?"),
            error_data.get("message", "No message"),
            error_data.get("stack", "")
        )
        return "", 204
    except Exception as e:
        app.logger.error("Failed to log JS error", exc_info=e)
        return "", 500

@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.error("Unhandled Exception", exc_info=e)
    return render_template("error.html", error=e), 500

if __name__ == "__main__":
    app.run(debug=True)
