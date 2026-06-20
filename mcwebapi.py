import subprocess
import json
import threading
import os
from datetime import datetime
from typing import Dict, Any
from urllib.parse import urlencode

ACTIVE_LISTENERS: Dict[str, Dict[str, Any]] = {}


def fetch_server_info(host: str, port: int, masterkey: str) -> tuple[bool, dict | str]:
    """Curls the /api/server endpoint on the minecraft server."""
    url = f"http://{host}:{port}/api/server"
    try:
        result = subprocess.run(
            [
                "curl",
                "-s",
                "-X",
                "GET",
                url,
                "-H",
                f"Authorization: Bearer {masterkey}",
                "-H",
                "Content-Type: application/json",
                "--max-time",
                "10",
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            return False, f"Curl failed: {result.stderr.strip()}"

        data = json.loads(result.stdout)
        return True, data

    except json.JSONDecodeError:
        return False, f"Invalid JSON response: {result.stdout.strip()}"
    except Exception as e:
        return False, f"Unexpected error: {e}"


def _safe_json(value: str):
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value


def _write_stream_to_file(proc: subprocess.Popen, output_file: str) -> None:
    dirpath = os.path.dirname(output_file)
    if dirpath:
        os.makedirs(dirpath, exist_ok=True)

    event_type = "message"
    data_lines: list[str] = []

    def flush_event(fh):
        nonlocal event_type, data_lines
        if not data_lines:
            return
        payload = "\n".join(data_lines)
        record = {
            "ts": datetime.utcnow().isoformat() + "Z",
            "event": event_type,
            "data": _safe_json(payload),
        }
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        fh.flush()
        event_type = "message"
        data_lines = []

    with open(output_file, "a", encoding="utf-8") as f:
        # always write a start marker so you know file path is correct
        f.write(
            json.dumps(
                {"ts": datetime.utcnow().isoformat() + "Z", "event": "listener_started"}
            )
            + "\n"
        )
        f.flush()

        if not proc.stdout:
            return

        for raw_line in proc.stdout:
            line = raw_line.rstrip("\r\n")

            if line == "":
                flush_event(f)
                continue

            # keepalive/comment line from SSE
            if line.startswith(":"):
                f.write(
                    json.dumps(
                        {
                            "ts": datetime.utcnow().isoformat() + "Z",
                            "event": "keepalive",
                            "data": line[1:].strip(),
                        }
                    )
                    + "\n"
                )
                f.flush()
                continue

            if line.startswith("event:"):
                event_type = line.split(":", 1)[1].strip() or "message"
            elif line.startswith("data:"):
                data_lines.append(line.split(":", 1)[1].lstrip())

        flush_event(f)


def start_event_listener(
    listener_id: str, host: str, port: int, masterkey: str, output_file: str
) -> tuple[bool, str]:
    if listener_id in ACTIVE_LISTENERS:
        p = ACTIVE_LISTENERS[listener_id]["proc"]
        if p.poll() is None:
            return False, "Listener already running."

    ALL_TYPES = "chat,command,join,leave,death,game"
    query = urlencode({"types": ALL_TYPES})
    url = f"http://{host}:{port}/api/events/stream?{query}"

    try:
        proc = subprocess.Popen(
            [
                "curl",
                "-N",  # no buffering (SSE)
                "-sS",  # silent but show errors
                url,
                "-H",
                f"Authorization: Bearer {masterkey}",
                "-H",
                "Accept: text/event-stream",
                "-H",
                "Cache-Control: no-cache",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0,  # unbuffered
        )

        # capture stderr in a separate thread so it doesnt block
        def log_stderr(p, out):
            if p.stderr:
                for line in p.stderr:
                    line = line.strip()
                    if line:
                        with open(out, "a") as f:
                            f.write(
                                json.dumps(
                                    {
                                        "ts": datetime.utcnow().isoformat() + "Z",
                                        "event": "curl_stderr",
                                        "data": line,
                                    }
                                )
                                + "\n"
                            )

        t = threading.Thread(
            target=_write_stream_to_file, args=(proc, output_file), daemon=True
        )
        t_err = threading.Thread(
            target=log_stderr, args=(proc, output_file), daemon=True
        )
        t.start()
        t_err.start()

        ACTIVE_LISTENERS[listener_id] = {
            "proc": proc,
            "thread": t,
            "thread_err": t_err,
            "output": output_file,
        }
        return True, f"Listener started. Logging to {output_file}"
    except Exception as e:
        return False, f"Failed to start listener: {e}"


def stop_event_listener(listener_id: str) -> tuple[bool, str]:
    entry = ACTIVE_LISTENERS.get(listener_id)
    if not entry:
        return False, "No listener running."

    proc = entry["proc"]
    try:
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                proc.kill()
        ACTIVE_LISTENERS.pop(listener_id, None)
        return True, "Listener stopped."
    except Exception as e:
        return False, f"Failed to stop listener: {e}"
