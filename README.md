# CMSC495_Capstone

This is a Flask-based web application that allows users to download videosfrom public YouTube playlists. It is intended for **educational and personal use only**.

> Disclaimer: This tool is not intended for downloading copyrighted content or bypassing YouTube’s Terms of Service. It only supports public videos and encourages users to download content they own or that is licensed for reuse.

---

## Features

- Download full YouTube playlists as MP4 (video)
- Playlist URL input
- Can search using keywords

---

## Technologies Used

- Python 3.x
- Flask
- yt-dlp 
- ffmpeg
- HTML/CSS
- JSON 

TODO:
- Sample progress bar or indicator of status
  Implimented the yt-dlp Python API
- Error Logging / risk mitications / Server and Clientside
  - Backend Logging: Already implemented!
    Errors are logged to logs/backend.log 
    via Python’s logging and TimedRotatingFileHandlerapp.
  - Client Logging: Already implemented!
    JavaScript window.onerror sends errors to /log_client_error, which logs to logs/client.log
- ✅ Discalmer review - shows first time (feature/videoDownloadProgressBar)
- Fix audio download
- -gmail or google account OAuth
- Playlist saving feature for differentiation of downloads (save by user specified groupings) 
  - create subfolders in designated download folder
- ✅ Chrome @media rules test environment for multiple form factors. Dreamweaver also an option. Intellij or Visual Code may have extension.
  See the media_rules_instructions.md file.

