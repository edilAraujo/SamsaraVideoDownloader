import datetime

import pytz

import SamsaraAPI


def convertTimeZone(tz):
    if tz == 'PDT' or tz == 'PST' or tz == 'Pacific Daylight Time' or tz == 'Pacific Standard Time':
        return 'US/Pacific'
    elif tz == 'EDT' or tz == 'EST' or tz == 'Eastern Daylight Time' or tz == 'Eastern Standard Time':
        return 'US/Eastern'
    elif tz == 'CDT' or tz == 'CST' or tz == 'Central Daylight Time' or tz == 'Central Standard Time':
        return 'US/Central'
    elif tz == 'MDT' or tz == 'MST' or tz == 'Mountain Daylight Time' or tz == 'Mountain Standard Time':
        return 'US/Mountain'
    elif tz == 'AKDT' or tz == 'AKST' or tz == 'Alaska Daylight Time' or tz == 'Alaska Standard Time':
        return 'US/Alaska'
    elif tz == 'HADT' or tz == 'HST' or tz == 'Hawaii Daylight Time' or tz == 'Hawaii Standard Time':
        return 'US/Hawaii'
    else:
        return 'UTC'


def convert_to_rfc(date_obj):
    # date_obj = datetime.datetime.strptime(date_str, '%m/%d/%Y')
    local_tz = pytz.timezone(convertTimeZone(str(datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo)))
    local_date_obj = local_tz.localize(date_obj, is_dst=None)
    rfc_date_str = local_date_obj.isoformat()

    return rfc_date_str


def convert_date(date_str, str_format='%b %d, %Y %I:%M:%S %p %Z'):
    date_time = datetime.datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%SZ')
    utc_time = pytz.utc.localize(date_time)
    local_timezone = pytz.timezone(convertTimeZone(
        str(datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo)))  # Replace with your local timezone
    local_time = utc_time.astimezone(local_timezone)
    formatted_date_str = datetime.datetime.strftime(local_time, str_format)
    return formatted_date_str


def get_user_dates():
    while True:
        try:
            date_input = input("Enter a date (MM/DD/YYYY): ").strip()
            time_input = input("Enter a time (HH:MM AM/PM): ").strip()
            duration_input = input("Enter a duration in minutes: ").strip()

            # Convert input to datetime object
            start_date = datetime.datetime.strptime(date_input + " " + time_input, "%m/%d/%Y %I:%M %p")

            # Convert duration to integer and calculate end time
            duration_minutes = int(duration_input)
            end_date = start_date + datetime.timedelta(minutes=duration_minutes)

            return convert_to_rfc(start_date), convert_to_rfc(end_date)
        except ValueError:
            print("Invalid date, time, or duration format. Please try again.")


def getAPIKey():
    while True:
        APIKEY = input("Enter a Samsara API key (e.g., samsara_api_0123456789): ").strip()

        # Perform input validation
        if is_valid_api_key(APIKEY):
            return APIKEY
        else:
            print("Invalid API key format. Please enter a valid API key.")


def is_valid_api_key(api_key):
    # Perform API key format validation (you can customize this based on Samsara's API key format)
    return api_key.startswith("samsara_api_") and len(api_key) == 42


def get_vehicle_id(api_key):
    """Retrieve vehicle ID based on user input."""
    try:
        vehicle_name = input("Enter the vehicle name: ").strip()

        vehicles = SamsaraAPI.getVehicles(api_key)
        if not vehicles:
            print("No vehicles found. Please check your API key and try again.")
            return None

        for vehicle in vehicles:
            if vehicle.get("name") and vehicle["name"].strip().lower() == vehicle_name.strip().lower():
                return vehicle.get("id")

        print("Vehicle not found. Please try again.")
    except Exception as e:
        print(f"An error occurred: {e}. Please check your API key and try again.")

    return None
