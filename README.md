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
- 🚨 **URGENT** Addent a UserGuide template with screen captures in a mark down format. Can be updated from another User Guide or be used as main User Guide. Mark Downn is lightweight and can be "packaged" with app as User Guide. [Theoretically]
Added the following [feature/errorLogging] branch:
- Added the following features:
  - Only registered users can download. User can conduct search, but instead of download button, it will read 'Login in to Download'. If they click it, the Login modal window will show.
  - Only registered users can see playlist
  - Disclaimer WILL show often just for testing purposes.
  - Worked on @media rules to ensure site works on iPhone XE size

- 🚨 **URGENT** Implimented the yt-dlp Python API. Had to rewrite application foundation code. All efforts did not allow video downloading.
- 🚨 **URGENT** Ensure that the .secrets folder is created with .env internal file with the API key.
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

NEXT FEATURES:
- ✅ Playlist - working
- - Playlist saving feature for differentiation of downloads (save by user specified groupings) 
  - create subfolders in designated download folder
  - ✅ Read from history, return search like view of previously downloaded content and show with a PLAY button.
  - ✅ Dropdown to either create a new playlist, or play from a previously created playlist
  - When downloading a video, prompt use to select what playlist to assign the video.
  - When videos are deleted from history, they should also be deleted from the playlist, and visa versa.


