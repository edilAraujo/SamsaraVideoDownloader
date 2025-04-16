Samsara Multi-Camera Video Retrieval Tool

Description:
  - This Python script automates the process of retrieving, downloading, and merging video footage from multiple Samsara camera angles (road-facing, driver-facing, analog) for a specified vehicle and time period. It aims to simplify the gathering of comprehensive visual evidence for incident reviews, compliance checks, or driver coaching by reducing the manual effort involved in handling individual video clips.

Features:
  - Automated Retrieval: Interfaces with the Samsara API to request video footage based on user-provided vehicle name, start time, and duration.
  - Multi-Camera Support: Requests and processes footage from road-facing, driver-facing, and analog camera inputs simultaneously.
  - Status Polling: Checks the status of retrieval requests and proceeds with downloading once footage is available.
  - Robust Downloading: Downloads video segments with basic retry logic and avoids re-downloading existing files.
  - Video Merging:
    - Concatenates individual one-minute clips into a single video file for each camera angle using moviepy.
    - Creates a final side-by-side video combining the merged footage from different angles.

Rate Limit Handling: 
  - Respects Samsara API rate limits using the ratelimit library.

Logging & Tracking: 
  - Logs operational details to a file and saves retrieval request IDs for tracking/debugging.

Requirements
Python 3.x

Samsara API Token with the following permissions:
  - Media Retrieval (Read & Write)
  - Vehicles (Read)

Python packages listed in requirements.txt.

Installation:
  Clone the repository or download the script files (main.py, helpers.py, SamsaraAPI.py).

  (Recommended) Create and activate a virtual environment:
    python -m venv venv
    
    # On Windows
    .\venv\Scripts\activate
    
    # On macOS/Linux
    source venv/bin/activate


Install the required packages:
  pip install -r requirements.txt

Usage
  Navigate to the script's directory in your terminal.

Run the main script:
  python main.py

Follow the prompts to enter:
- Your Samsara API Key
- The exact Vehicle Name
- The Start Date and Time (format: MM/DD/YYYY HH:MM in 24-hour format, e.g., 04/16/2025 13:30)
- The Duration in minutes for which to retrieve video.

The script will then begin the process of requesting, polling, downloading, and merging the videos. Progress and any errors will be logged.

File Structure
.
├── main.py             # Main script execution, orchestration
├── helpers.py          # Helper functions for input, validation, time conversion
├── SamsaraAPI.py       # Wrapper for Samsara API interactions
├── requirements.txt    # Project dependencies
├── Logs/               # Directory for log files and request ID JSON files
│   ├── VideoRetrievalActivity_YYYY-MM-DD_HH-MM-SS.log
│   └── request_ids_YYYY-MM-DD_HH-MM-SS.json
└── Videos/             # Directory for downloaded and merged videos
    ├── Road_VideoClip_....mp4
    ├── Driver_VideoClip_....mp4
    ├── Analog_VideoClip_....mp4
    ├── Road_Merged_....mp4
    ├── Driver_Merged_....mp4
    ├── Analog_Merged_....mp4
    └── SideBySide_Merged_....mp4

Outputs:
- Log File: Detailed activity log created in the Logs/ directory.
- Request ID File: JSON file containing the Samsara retrieval IDs created in the Logs/ directory.
- Video Files: Downloaded individual clips, merged videos per camera, and the final side-by-side video are saved in the Videos/ directory.


Known Issues / Limitations:
- Video download times can vary significantly based on vehicle connectivity and status. The script polls periodically but completion time is dependent on Samsara processing and vehicle upload.
- Interrupting the script (e.g., Ctrl+C) before downloads and merges are complete will stop the process. Re-running the script will initiate new retrieval requests for the same period; it does not currently resume based on the saved request_ids.json.
- Only high-res videos and camera connector are supported at this time. Other types of media (e.g. hyperlapse, low-res) are planned to be supported in the future.
- Currently, only unblurred media without any of the telematics data (timestamp /vehicle speed) is supported.
- Quota limits (900,000 seconds or 250hrs of high-res footage) are enforced.
