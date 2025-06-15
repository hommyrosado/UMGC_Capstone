import webbrowser
import requests
import os
import re
import subprocess
import glob

from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, send_file, abort

# TODO [Hommy, 2025-05-29]: Add error logging capabilities.
# TODO [Hommy, 2025-05-29]: Examine vulnerabilities for risk mitigation.

# Initialize Flask app
app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
YOUTUBE_SEARCH_URL = 'https://www.googleapis.com/youtube/v3/search'
DOWNLOAD_FOLDER = 'downloads'

# Create a download folder if it doesn't already exist
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/', methods=['GET', 'POST'])
def index():
    videos = []

    if request.method == 'POST':
        # Get search input and clean it up
        query = request.form['query'].strip()

        # Check if the query is a YouTube video URL
        match = re.search(r"(?:v=|youtu\.be/)([\w-]{11})", query)
        if match:
            # --- Handle YouTube link input ---
            video_id = match.group(1)
            video_api_url = 'https://www.googleapis.com/youtube/v3/videos'
            params = {
                'part': 'snippet,status',
                'id': video_id,
                'key': YOUTUBE_API_KEY
            }

            # Make request to YouTube Data API
            response = requests.get(video_api_url, params=params)
            if response.status_code == 200:
                data = response.json()
                if data['items']:
                    video_data = data['items'][0]
                    status = video_data.get('status', {})
                    license_type = status.get('license', 'unknown')

                    # Ensure video is Creative Commons licensed
                    if license_type != 'creativeCommon':
                        print("Video is not Creative Commons")
                        return render_template('index.html', videos=[])

                    # Append video details to be displayed on the frontend
                    video = {
                        'title': video_data['snippet']['title'],
                        'thumbnail': video_data['snippet']['thumbnails']['medium']['url'],
                        'video_id': video_id,
                        'video_url': f"https://www.youtube.com/watch?v={video_id}"
                    }
                    videos.append(video)
            else:
                print("API error:", response.text)

        else:
            # --- Handle keyword-based search ---
            search_params = {
                'part': 'snippet',
                'q': query,
                'key': YOUTUBE_API_KEY,
                'maxResults': 10,
                'type': 'video',
                'videoLicense': 'creativeCommon'  # Only return Creative Commons videos
            }

            # Make search request
            response = requests.get(YOUTUBE_SEARCH_URL, params=search_params)
            if response.status_code == 200:
                data = response.json()
                for item in data['items']:
                    video_id = item['id']['videoId']
                    video = {
                        'title': item['snippet']['title'],
                        'thumbnail': item['snippet']['thumbnails']['medium']['url'],
                        'video_id': video_id,
                        'video_url': f"https://www.youtube.com/watch?v={video_id}"
                    }
                    videos.append(video)
            else:
                print("API error:", response.text)

    # Render template with list of videos (if any)
    return render_template('index.html', videos=videos)

@app.route('/downloads/<video_id>')
def download(video_id):
    # Build the video URL
    video_url = f"https://www.youtube.com/watch?v={video_id}"

    # Command to download the best available video format using yt-dlp
    download_cmd = [
        'yt-dlp',
        '-f', 'best',
        video_url,
        '-o', os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s')
    ]

    try:
        # Execute the download command
        subprocess.run(download_cmd, check=True)

        # Find the most recently downloaded file
        list_of_files = glob.glob(os.path.join(DOWNLOAD_FOLDER, '*'))
        if not list_of_files:
            return "No files found", 404

        latest_file = max(list_of_files, key=os.path.getctime)
        print("Sending file: ", latest_file)

        # Send file to client for download
        return send_file(latest_file, as_attachment=True)

    except subprocess.CalledProcessError:
        return "Download failed", 500
    except Exception as e:
        print("Unexpected error:", e)
        abort(500)

if __name__ == '__main__':
    # Automatically open the browser on launch
    webbrowser.open('http://127.0.0.1:80')
    app.run(port=80)
