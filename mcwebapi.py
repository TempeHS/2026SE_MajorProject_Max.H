import os
import json
import requests
import subprocess
import database_manager
import shlex


def check_server_connection(serverID: int, userID: int) -> tuple[bool, str]:
    """
    Fetches server connection details from the DB and pings the MCRestAPI.
    Returns (True, "online") or (False, reason).
    """
    ok, details, msg = database_manager.get_server_connection_details(serverID, userID)
    if not ok:
        return False, msg

    host = details["serverHost"]
    port = details["serverPort"]
    key = details["serverKey"]  # decrypted master key from Fernet

    url = f"http://{host}:{port}/api/server"
    headers = {"Authorization": f"Bearer {key}"}

    try:
        response = requests.get(url, headers=headers, timeout=5)

        if response.status_code == 200:
            return True, "online"
        elif response.status_code == 401:
            return False, "Authentication failed — check master key"
        elif response.status_code == 403:
            return False, "Forbidden — key lacks server.read permission"
        else:
            return False, f"Unexpected status: {response.status_code}"

    except requests.ConnectionError:
        return False, "Could not connect — server may be offline or unreachable"
    except requests.Timeout:
        return False, "Connection timed out"
    except Exception as e:
        return False, f"Unexpected error: {e}"


def build_mcrest_curl_command(
    serverHost: str, serverPort: int, serverKey: str, timeout: int = 5
) -> str:
    """
    Build curl command for MCRestAPI health check:
    GET /api/server with Bearer auth header.
    """
    url = f"http://{serverHost}:{serverPort}/api/server"
    cmd = [
        "curl",
        "-sS",
        "-m",
        str(timeout),
        "-H",
        f"Authorization: Bearer {serverKey}",
        url,
    ]
    return " ".join(shlex.quote(part) for part in cmd)
