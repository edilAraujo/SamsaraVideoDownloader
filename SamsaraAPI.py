import requests
from ratelimit import limits, sleep_and_retry

# Limit to 100 calls per 60 seconds
CALLS_PER_MINUTE = 100


def getVehicles(api_token, tag_ids=''):
    url = f"https://api.samsara.com/fleet/vehicles?limit=512&tagIds={tag_ids}"

    headers = {"Authorization": "Bearer " + api_token}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Error: {response.text}")

    vehicles = response.json()["data"]
    hasnext = response.json()["pagination"]["hasNextPage"]

    while hasnext:
        pagination_url = url + "&after=" + response.json()["pagination"]["endCursor"]
        response = requests.get(pagination_url, headers=headers)

        if response.status_code != 200:
            raise Exception(f"Error: {response.text}")

        vehicles += response.json()["data"]
        hasnext = response.json()["pagination"]["hasNextPage"]

    return vehicles


@sleep_and_retry
@limits(calls=CALLS_PER_MINUTE, period=60)
def createMediaRetrievalRequest(api_token, startTime, endTime, vehicleID, mediaType='videoHighRes', inputs=None):
    if inputs is None:
        inputs = ['dashcamRoadFacing', 'dashcamDriverFacing', 'analog1']

    url = "https://api.samsara.com/cameras/media/retrieval"

    payload = {
        "mediaType": mediaType,
        "inputs": inputs,
        "endTime": endTime,
        "startTime": startTime,
        "vehicleId": vehicleID
    }

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": "Bearer " + api_token
    }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 200:
        print(response.text)
        raise Exception(f"Error: {response.text}")

    return response.json()


@sleep_and_retry
@limits(calls=CALLS_PER_MINUTE, period=60)
def getMediaRetrievalDetails(api_token, retrieval_id):
    url = f"https://api.samsara.com/cameras/media/retrieval?retrievalId={retrieval_id}"

    headers = {
        "accept": "application/json",
        "authorization": "Bearer " + api_token
    }

    response = requests.get(url, headers=headers)
    # if response.status_code != 200:
    #     raise Exception(f"Error: {response.text}")

    return response
