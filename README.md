# 🚚 Samsara Multi-Camera Video Retrieval Tool

## 📌 Description

This Python tool automates the process of retrieving, downloading, and merging video footage from multiple Samsara camera angles—road-facing, driver-facing, and analog—for a specified vehicle and time period. It's designed to streamline evidence collection for incident reviews, compliance checks, and driver coaching by reducing the manual effort required to manage individual video clips.

---

## ✨ Features

- **Automated Retrieval**  
  Interfaces with the Samsara API to request footage based on vehicle name, start time, and duration.

- **Multi-Camera Support**  
  Simultaneously requests and processes road-facing, driver-facing, and analog camera feeds.

- **Status Polling**  
  Polls the API to check the status of video requests and proceeds with downloading once available.

- **Resilient Downloading**  
  Implements basic retry logic and avoids re-downloading files that already exist.

- **Video Merging**  
  - Concatenates one-minute video clips into a single file per camera using `moviepy`.
  - Produces a final side-by-side composite video from the merged footage.

- **Rate Limit Handling**  
  Uses the `ratelimit` library to respect Samsara API rate limits.

- **Logging & Tracking**  
  Logs operational activity to file and saves request IDs for future reference or debugging.

---

## 🛠 Requirements

- Python 3.x  
- A **Samsara API Token** with the following permissions:
  - Media Retrieval (Read & Write)
  - Vehicles (Read)

---

## ⚙️ Installation

Clone the repository or download the script files (`main.py`, `helpers.py`, `SamsaraAPI.py`).

**(Recommended)** Set up a virtual environment:

```bash
python -m venv venv

# On Windows
.\venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate


Install the required packages:
  pip install -r requirements.txt

Usage
  Navigate to the script directory in your terminal.

Run the main script:
  python main.py

Follow the prompts to enter:
- Your Samsara API Key
- The exact Vehicle Name
- The Start Date and Time (format: MM/DD/YYYY HH:MM in 24-hour format, e.g., 04/16/2025 13:30)
- The Duration in minutes for which to retrieve video.

The script will then begin the process of requesting, polling, downloading, and merging the videos. Progress and any errors will be logged.
```

### File Structure
```
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
```

---

## 📤 Output Files
- **Logs/**  
  Contains detailed logs of each run and JSON files with API request IDs.
- **Videos/**  
  Includes raw one-minute clips, merged videos per camera angle, and a final side-by-side composite video.


---

## ⚠️ Known Issues / Limitations
- **Variable Completion Time**  
  Video availability depends on vehicle connectivity and Samsara’s backend processing. Expect delays in some cases.
- **No Resume Support**  
  If interrupted (e.g., Ctrl+C), the script will start fresh on the next run and issue new retrieval requests.
- **Media Type Limitations**  
  Currently supports only unblurred, high-resolution footage without timestamp/telematics overlays. Support for hyperlapse and low-res video is planned.
- **Quota Limits****  
  Samsara enforces limits (900,000 seconds / ~250 hours of high-res footage per month).
