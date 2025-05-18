import webbrowser
import requests
import os

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
        params = {
            'part': 'snippet',
            'q': query,
            'key': YOUTUBE_API_KEY,
            'maxResults': 10,
            'type': 'video',
            'videoLicense': 'creativeCommon'
        }
        response = requests.get(YOUTUBE_SEARCH_URL, params=params)
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
