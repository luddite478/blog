import requests
import os

STREAM_PULL_INTERNAL_ADDRESS = os.environ.get('STREAM_PULL_INTERNAL_ADDRESS')

def is_stream_live():
    try:
        response = requests.head(STREAM_PULL_INTERNAL_ADDRESS, timeout=2)
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return False