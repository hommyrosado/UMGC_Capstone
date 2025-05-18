import webbrowser
import requests
import os
import re

from pytube import YouTube
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, send_file

app = Flask(__name__)
load_dotenv()
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
YOUTUBE_SEARCH_URL = 'https://www.googleapis.com/youtube/v3/search'
DOWNLOAD_FOLDER = 'downloads'

# Create downloads folder if it doesn't exist
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/', methods=['GET', 'POST'])
def index():
    videos = []
    if request.method == 'POST':
        query = request.form['query']

        #validate input
        match = re.search(r"(?:v=|youtu\.be/)([\w-]{11})", query)
        if not match:
            print("Invalid YouTube URL")
            return render_template('index.html', videos = [])

        video_id = match.group(1)

        #call video endpoint at youtube
        video_api_url = 'https://www.googleapis.com/youtube/v3/videos'
        params = {
            'part': 'snippet,contentDetails,status',
            'id': video_id,
            'key': YOUTUBE_API_KEY
        }

        response = requests.get(video_api_url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data['items']:
                video_data = data['items'][0]
                license_type = video_data['status'].get('license')

                if license_type != "creativeCommon":
                    print("Video is not available for download")
                    return render_template('index.html', videos = [])

                video = {
                    'title': video_data['snippet']['title'],
                    'thumbnail': video_data['snippet']['thumbnails']['medium']['url'],
                    'video_id': video_id,
                    'video_url': f"https://www.youtube.com/watch?v={video_id}"
                }
                videos.append(video)
            else:
                print("Video not found")
        else:
            print("API error:", response.text)
    return render_template('index.html', videos=videos)

@app.route('/download/<video_id>')
def download(video_id):
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    yt = YouTube(video_url)
    stream = yt.streams.get_highest_resolution()
    output_path = stream.download(output_path=DOWNLOAD_FOLDER)
    return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    webbrowser.open('http://127.0.0.1:80')
    app.run(port=80)
