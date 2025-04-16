import datetime
import json
import logging
import os
import random
import re
import sys
import time
from time import sleep

import requests
from moviepy import VideoFileClip, concatenate_videoclips, clips_array, vfx

import SamsaraAPI
import helpers


def sanitize_filename(filename):
    """Sanitize filename to ensure it doesn't contain any invalid characters for the file system."""
    return re.sub(r'[<>:"/\\|?*]', '_', filename)


# Setup logging
def setup_logging():
    """Initialize logging configuration."""
    base_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
    log_folder = os.path.join(base_dir, "Logs")
    video_folder = os.path.join(base_dir, "Videos")

    os.makedirs(log_folder, exist_ok=True)
    os.makedirs(video_folder, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_filename = os.path.join(log_folder, f'VideoRetrievalActivity_{timestamp}.log')

    logging.basicConfig(
        filename=log_filename,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logging.info("Logging initialized successfully.")
    return base_dir, log_folder, video_folder


# Function to send video requests
def send_video_request(api_key):
    """Request video retrieval from the Samsara API."""
    user_dates = helpers.get_user_dates()
    vehicle_id = helpers.get_vehicle_id(api_key)

    start_time = datetime.datetime.fromisoformat(user_dates[0])
    end_time = datetime.datetime.fromisoformat(user_dates[1])

    request_ids = []
    current_time = start_time

    while current_time <= end_time:
        try:
            video_request = SamsaraAPI.createMediaRetrievalRequest(
                api_key,
                current_time.isoformat(),
                (current_time + datetime.timedelta(minutes=1)).isoformat(),
                vehicle_id
            )

            retrieval_id = video_request.get("data", {}).get("retrievalId")
            if retrieval_id:
                logging.info(f"Requested video at {current_time.isoformat()}, ID: {retrieval_id}")
                request_ids.append([current_time.isoformat(), retrieval_id])
            else:
                logging.error(f"Invalid response for {current_time.isoformat()}")
        except Exception as e:
            logging.error(f"Skipping failed request at {current_time.isoformat()}: {e}")

        current_time += datetime.timedelta(minutes=1)

    return request_ids


# Function to download a video
def download_video(url, filename):
    """Download video from the provided URL with retry logic."""
    retries = 3
    for attempt in range(retries):
        try:
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                with open(filename, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)
                logging.info(f"Downloaded: {filename}")
                return True
            else:
                logging.error(f"Failed to download {url}, Status: {response.status_code}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Download error ({attempt + 1}/{retries}): {e}")
        sleep(random.uniform(1, 3))  # Wait before retrying

    logging.error(f"Failed to download {url} after {retries} attempts.")
    return False


# Function to process video retrieval status
def process_media_info(request_ids, api_key, video_folder):
    """Check video retrieval status and download videos when available."""
    road_videos, driver_videos, analog = [], [], []

    while True:
        print("\nChecking video statuses...")
        all_complete = True

        for r_id in request_ids:
            request_status = SamsaraAPI.getMediaRetrievalDetails(api_key, r_id[1])

            if request_status.status_code == 200:  # workaround for issue with internal server errors from the endpoint
                request_status = request_status.json()
                media_list = request_status.get("data", {}).get("media", [])
                for media_info in media_list:
                    if media_info["status"] == "available":
                        if media_info["input"] == "dashcamRoadFacing":
                            media_type = "road"
                        elif media_info["input"] == "dashcamDriverFacing":
                            media_type = 'driver'
                        else:
                            media_type = 'analog1'
                        filename = os.path.join(video_folder, sanitize_filename(f"{r_id[0]}_{media_type}.mp4"))

                        if not os.path.exists(filename):
                            print(f"Downloading {media_type} video for {r_id[0]}...")
                            url = media_info["urlInfo"]["url"]
                            if download_video(url, filename):
                                if media_type == "road":
                                    road_videos.append(filename)
                                elif media_type == "driver":
                                    driver_videos.append(filename)
                                else:
                                    analog.append(filename)
                            else:
                                all_complete = False
                        else:
                            continue  # Skip already downloaded files
                    else:
                        logging.info(f"Video {r_id[0]} is still processing...")
                        all_complete = False
            else:
                logging.error(f'API error: {request_status.status_code} - {request_status.text}: {r_id[0]} - {r_id[1]}')
                print(f'API error:  {request_status.status_code} - {request_status.text}: {r_id[0]} - {r_id[1]}')

        if all_complete:
            print("All videos are now available.")
            break

        print("Waiting 3 minutes before checking again...")
        logging.info("Waiting 3 minutes before checking again...")
        time.sleep(180)

    return road_videos, driver_videos, analog


# Function to merge videos
def merge_videos(video_list, output_file):
    """Merge multiple videos sequentially if more than one exists."""
    if len(video_list) > 1:
        concatenated = concatenate_videoclips([VideoFileClip(v) for v in video_list])
        concatenated.write_videofile(output_file, codec="libx264", fps=24)
        return output_file
    return video_list[0] if video_list else None


def merge_videos_side_by_side(video_folder, request_ids, road_videos, driver_videos, analog_videos):
    """Merge road, driver, and analog videos sequentially, then combine them side by side if present."""

    def get_output_filename(video_type):
        return os.path.join(video_folder,
                            sanitize_filename(f"{video_type}_merged_{request_ids[0][0]}_to_{request_ids[-1][0]}.mp4"))

    def resize_clip(clip, new_width=1920, new_height=1080):
        return clip.with_effects([vfx.Resize((new_width, new_height))])

    # Merge each type of video sequentially
    merged_road = merge_videos(road_videos, get_output_filename("road")) if road_videos else None
    merged_driver = merge_videos(driver_videos, get_output_filename("driver")) if driver_videos else None
    merged_analog = merge_videos(analog_videos, get_output_filename("analog")) if analog_videos else None

    if not merged_road:
        logging.error("No road videos provided. Aborting merge.")
        print("No road videos provided. Aborting merge.")
        return None

    # If no driver or analog videos exist, return only the merged road video
    if not merged_driver and not merged_analog:
        logging.info(f"No driver or analog videos found. Returning merged road video: {merged_road}")
        print(f"No driver or analog videos found. Returning merged road video: {merged_road}")
        return merged_road

    road_clip, driver_clip, analog_clip = None, None, None  # Initialize variables

    try:
        road_clip = VideoFileClip(merged_road).without_audio()
        driver_clip = VideoFileClip(merged_driver).without_audio() if merged_driver else None
        analog_clip = VideoFileClip(merged_analog).without_audio() if merged_analog else None

        # Determine target resolution (largest width & height among clips)
        target_width = road_clip.w
        target_height = road_clip.h

        # Determine the shortest duration
        min_duration = min(clip.duration for clip in [road_clip, driver_clip, analog_clip] if clip)

        # Trim videos to match the shortest one
        road_clip = road_clip.subclipped(0, min_duration)
        if driver_clip:
            driver_clip = driver_clip.subclipped(0, min_duration)
        if analog_clip:
            analog_clip = analog_clip.subclipped(0, min_duration)

        clips = [road_clip]

        # Resize all clips to match the target resolution
        # road_clip = resize_clip(road_clip, target_size)
        if driver_clip:
            driver_clip = resize_clip(driver_clip, target_width, target_height)
            clips.append(driver_clip)
        if analog_clip:
            analog_clip = resize_clip(analog_clip, target_width, target_height)
            clips.append(analog_clip)

        if driver_clip or analog_clip:
            # Merge side by side
            final_clip = clips_array([clips])
            final_output = os.path.join(video_folder, sanitize_filename(
                f"final_merged_{request_ids[0][0]}_to_{request_ids[-1][0]}.mp4"))

            final_clip.write_videofile(final_output, codec="libx264", fps=24)

            logging.info(f"Final video merged successfully into {final_output}")
            print(f"Final video merged successfully into {final_output}")
            return final_output

        return merged_road
    except Exception as e:
        logging.error(f"Error merging final side-by-side video: {e}")
        print(f"Error merging final side-by-side video: {e}")
        return None
    finally:
        # Explicitly close clips to prevent errors on shutdown
        for clip in [road_clip, driver_clip, analog_clip]:
            if clip:
                clip.close()


# Function to process already downloaded videos. For internal use only. Need to change the camera angle as needed
def process_already_downloaded(request_ids, video_folder, cameraAngle='dashcamRoadFacing'):
    road_videos, driver_videos, analog = [], [], []

    while True:
        print("\nChecking video statuses...")
        all_complete = True

        for r_id in request_ids:
            if cameraAngle == "dashcamRoadFacing":
                media_type = "road"
            elif cameraAngle == "dashcamDriverFacing":
                media_type = 'driver'
            else:
                media_type = 'analog1'
            filename = os.path.join(video_folder, sanitize_filename(f"{r_id[0]}_{media_type}.mp4"))

            if os.path.exists(filename):
                if media_type == "road":
                    road_videos.append(filename)
                elif media_type == "driver":
                    driver_videos.append(filename)
                else:
                    analog.append(filename)
        if all_complete:
            print("All videos are now available.")
            break

        print("Waiting 3 minutes before checking again...")
        logging.info("Waiting 3 minutes before checking again...")
        time.sleep(180)

    return road_videos, driver_videos, analog


# Main execution function
def main():
    """debugging variables"""
    # api_key = ''

    # request_ids = [
    #     ["2025-03-23T04:00:00-07:00", "ceae878a-13cb-4bfb-9253-db768fd8394c"],
    #     ["2025-03-23T04:01:00-07:00", "ea13f8ac-276c-4117-9bd9-995e9516da91"],
    #     ["2025-03-23T04:02:00-07:00", "416c2237-f167-497c-a7e7-fada36228864"],
    #     ["2025-03-23T04:03:00-07:00", "90c74835-8a4e-405c-aeab-e8f666b87124"]
    # ]

    base_dir, log_folder, video_folder = setup_logging()

    api_key = helpers.getAPIKey()
    request_ids = send_video_request(api_key)

    if not request_ids:
        logging.error("No video requests could be made.")
        return

    print("\nSent video requests.")

    # Save requests in the same directory as log files
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = os.path.join(log_folder, f'request_ids_{timestamp}.json')
    try:
        with open(log_file, "r", encoding="utf-8") as file:
            existing_data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        existing_data = []
    existing_data.extend(request_ids)
    with open(log_file, "w", encoding="utf-8") as file:
        json.dump(existing_data, file, indent=4)

    # Process video downloads
    road_videos, driver_videos, analog_videos = process_media_info(request_ids, api_key, video_folder)

    # Process already downloaded videos (Internal testing)
    # road_videos, driver_videos, analog_videos = process_already_downloaded(request_ids, video_folder)

    # Merge videos if needed
    merge_videos_side_by_side(video_folder, request_ids, road_videos, driver_videos, analog_videos)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        print(f"Unexpected error: {e}")
    finally:
        input("Press Enter to exit...")
