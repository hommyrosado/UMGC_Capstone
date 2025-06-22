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
- yt-dlp [changed to yt_dlp]
- ffmpeg
- HTML/CSS
- JSON 

TODO:
Added the following [feature/errorLogging] branch:
- 🚨 **URGENT** Implimented the yt-dlp Python API. Had to rewrite application foundation code. All efforts did not allow video downloading.
- ✅ History folder to document history of downloaded videos. This JSON file is read, and if the video in the search results has already been downloaded, then a check mark indicator (or any we deam appropriate) shows in the results. This will help for the creation of a Playlist
- ✅ Sample progress bar or indicator of status. This progress bar shows up in a modal (popup) window that prompts the user to ensure that they "really" want to download the selected video.
- ✅ Error Logging for application side and client side code.
- TODO: Use this error logging for TESTING UAT and API vulnerability risk mitications / Server and Clientside
  - ✅ Backend Logging: Already implemented!
    Errors are logged to logs/backend.log 
    via Python’s logging and TimedRotatingFileHandlerapp.
- ✅ Client Logging: Already implemented!
    JavaScript window.onerror sends errors to /log_client_error, which logs to logs/client.log
- ✅ Discalmer review - shows first time (feature/videoDownloadProgressBar)
- ✅ Chrome @media rules test environment for multiple form factors. Dreamweaver also an option. Intellij or Visual Code may have extension.
  See the media_rules_instructions.md file.
  
- Playlist - working
- - NOT SURE? Playlist saving feature for differentiation of downloads (save by user specified groupings) 
  - NOT SURE? create subfolders in designated download folder

- Data file: playlists.json / history: download_history.json / logs: applog
-   All these need to be cleared upon NEW install. Even if this is a web-app, need to identify "New User" vs Returning user.


