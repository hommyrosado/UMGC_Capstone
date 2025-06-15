from yt_dlp import YoutubeDL
import os

# Replace with your desired test video
TEST_VIDEO_URL = "https://www.youtube.com/watch?v=xfq68R-4p3E"  # Safe for testing

# Set output directory
OUTPUT_DIR = "yt_test_downloads"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# yt-dlp options
ydl_opts = {
    'format': 'best',
    'outtmpl': os.path.join(OUTPUT_DIR, '%(title)s.%(ext)s')
}

def download_video(url):
    print(f"Starting download for: {url}")
    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print("✅ Download complete.")
    except Exception as e:
        print(f"❌ Download failed: {e}")

if __name__ == "__main__":
    download_video(TEST_VIDEO_URL)
