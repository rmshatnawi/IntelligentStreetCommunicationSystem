# # ============================================================
# # Project:  Intelligent Street Communication System (ISCS)
# # File:     RSU_Simulator/core/publisher.py
# # Author:   Raghad Shatnawi
# # Date:     March 2026
# # Purpose:  Handles sending signals from the RSU Simulator
# #           to the FastAPI server via HTTP POST requests.
# #           Each RSU uses this to publish its detected data.
# # ============================================================

# import requests
# import json


# # ─── publish_signal() ───────────────────────────────────────
# # Sends one signal to the server's /ingest endpoint.
# # Called by each RSU every time it detects vehicles.
# #
# # Parameters:
# #   server_url — full URL of the server e.g. http://localhost:8000
# #   signal     — dictionary containing the signal data
# #
# # Returns:
# #   True if server accepted the signal
# #   False if something went wrong
# def publish_signal(server_url: str, signal: dict) -> bool:
#     try:
#         # ─── Build the full endpoint URL ──────────────────
#         url = f"{server_url}/ingest"

#         # ─── Send the POST request ────────────────────────
#         # timeout=5 means if server doesn't respond in 5 seconds
#         # we give up and return False instead of freezing forever
#         response = requests.post(
#             url,
#             json=signal,           # automatically sets Content-Type to application/json
#             timeout=5
#         )

#         # ─── Check the response ───────────────────────────
#         if response.status_code == 200:
#             print(f"[OK]    Signal sent → segment: {signal.get('segment')} | speed: {signal.get('speed')} km/h")
#             return True
#         else:
#             print(f"[FAIL]  Server rejected signal → status: {response.status_code} | response: {response.text}")
#             return False

#     except requests.exceptions.ConnectionError:
#         # server is not running or wrong URL
#         print(f"[ERROR] Cannot connect to server at {server_url}")
#         return False

#     except requests.exceptions.Timeout:
#         # server took too long to respond
#         print(f"[ERROR] Server timeout at {server_url}")
#         return False

#     except Exception as e:
#         print(f"[ERROR] Unexpected error while sending signal: {e}")
#         return False

# ============================================================
# Project:  Intelligent Street Communication System (ISCS)
# File:     RSU_Simulator/core/publisher.py
# Purpose:  Sends RSU detection events and traffic-light state
#           to the FastAPI server via HTTP POST. Fails gracefully
#           if the server or an endpoint is unavailable.
# ============================================================

import requests


def publish_signal(server_url: str, signal: dict, endpoint: str = "/ingest") -> bool:
    """POST one RSU detection event to the server."""
    url = f"{server_url}{endpoint}"
    try:
        response = requests.post(url, json=signal, timeout=5)
        if response.status_code == 200:
            print(f"[OK]    {signal.get('rsu_id')} | {signal.get('plate_number')} "
                  f"| {signal.get('speed')} km/h")
            return True
        print(f"[FAIL]  Server rejected event → status: {response.status_code} | {response.text}")
        return False
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] Cannot connect to server at {server_url}")
        return False
    except requests.exceptions.Timeout:
        print(f"[ERROR] Server timeout at {server_url}")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error while sending event: {e}")
        return False


def publish_light_state(server_url: str, light_object: dict, endpoint: str = "/light") -> bool:
    """POST the traffic-light map object / state change to the server."""
    url = f"{server_url}{endpoint}"
    try:
        response = requests.post(url, json=light_object, timeout=5)
        if response.status_code == 200:
            print(f"[LIGHT] {light_object.get('light_id')} state sent → {light_object.get('state')}")
            return True
        print(f"[FAIL]  Light endpoint rejected → status: {response.status_code}")
        return False
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] Cannot connect to light endpoint at {url}")
        return False
    except requests.exceptions.Timeout:
        print(f"[ERROR] Light endpoint timeout at {url}")
        return False
    except Exception as e:
        print(f"[ERROR] Unexpected error while sending light state: {e}")
        return False