import webbrowser
import requests
import os
import re
import subprocess
import glob
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, send_file, abort, jsonify

app = Flask(__name__)
load_dotenv()

# Directories
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
YOUTUBE_SEARCH_URL = 'https://www.googleapis.com/youtube/v3/search'
DOWNLOAD_FOLDER = 'downloads'
LOG_FOLDER = 'logs'

# Create folders if not exist
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
os.makedirs(LOG_FOLDER, exist_ok=True)

# Backend Logger Setup
backend_logger = logging.getLogger('backend')
backend_logger.setLevel(logging.ERROR)
handler = TimedRotatingFileHandler(f"{LOG_FOLDER}/backend.log", when="midnight", interval=1)
handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
handler.suffix = "%Y-%m-%d"
backend_logger.addHandler(handler)

# Client Logger Setup
client_logger = logging.getLogger('client')
client_logger.setLevel(logging.INFO)
client_handler = TimedRotatingFileHandler(f"{LOG_FOLDER}/client.log", when="midnight", interval=1)
client_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
client_handler.suffix = "%Y-%m-%d"
client_logger.addHandler(client_handler)

@app.route('/', methods=['GET', 'POST'])
def index():
    videos = []
    try:
        if request.method == 'POST':
            query = request.form['query'].strip()
            match = re.search(r"(?:v=|youtu\.be/)([\w-]{11})", query)

            if match:
                video_id = match.group(1)
                video_api_url = 'https://www.googleapis.com/youtube/v3/videos'
                params = {
                    'part': 'snippet,status',
                    'id': video_id,
                    'key': YOUTUBE_API_KEY
                }
                response = requests.get(video_api_url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    if data['items']:
                        video_data = data['items'][0]
                        license_type = video_data.get('status', {}).get('license', 'unknown')
                        if license_type != 'creativeCommon':
                            return render_template('index.html', videos=[])
                        videos.append({
                            'title': video_data['snippet']['title'],
                            'thumbnail': video_data['snippet']['thumbnails']['medium']['url'],
                            'video_id': video_id,
                            'video_url': f"https://www.youtube.com/watch?v={video_id}"
                        })
                else:
                    backend_logger.error(f"API error: {response.text}")
            else:
                search_params = {
                    'part': 'snippet',
                    'q': query,
                    'key': YOUTUBE_API_KEY,
                    'maxResults': 10,
                    'type': 'video',
                    'videoLicense': 'creativeCommon'
                }
                response = requests.get(YOUTUBE_SEARCH_URL, params=search_params)
                if response.status_code == 200:
                    data = response.json()
                    for item in data['items']:
                        video_id = item['id']['videoId']
                        videos.append({
                            'title': item['snippet']['title'],
                            'thumbnail': item['snippet']['thumbnails']['medium']['url'],
                            'video_id': video_id,
                            'video_url': f"https://www.youtube.com/watch?v={video_id}"
                        })
                else:
                    backend_logger.error(f"API search error: {response.text}")
    except Exception as e:
        backend_logger.exception("Exception in index route")
        abort(500)
    return render_template('index.html', videos=videos)

@app.route('/download/<video_id>')
def download(video_id):
    try:
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        # Examine code with '-f' as opposed to 'f'
        download_cmd = [
            'yt-dlp', '-f', 'best', video_url,
            '-o', os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s')
        ]
        subprocess.run(download_cmd, check=True)

        files = glob.glob(os.path.join(DOWNLOAD_FOLDER, '*'))
        if not files:
            return "No files found", 404
        latest = max(files, key=os.path.getctime)
        return send_file(latest, as_attachment=True)
    except subprocess.CalledProcessError:
        backend_logger.exception("Download failed")
        return "Download failed", 500
    except Exception as e:
        backend_logger.exception("Unexpected error in download route")
        abort(500)

@app.route('/log_client_error', methods=['POST'])
def log_client_error():
    data = request.get_json()
    client_logger.info(f"Client error: {data}")
    return jsonify(status="logged"), 200

if __name__ == '__main__':
    webbrowser.open('http://127.0.0.1:80')
    app.run(port=80)
