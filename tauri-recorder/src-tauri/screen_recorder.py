#!/usr/bin/env python3
"""
SiC Screen Recorder - Python Backend

Handles screen recording using ffmpeg on macOS.
Uses PID file for state management across process calls.
"""

import sys
import json
import subprocess
import os
import signal
from datetime import datetime
from pathlib import Path

# State files
STATE_DIR = Path.home() / ".sic-screen-recorder"
PID_FILE = STATE_DIR / "recording.pid"
OUTPUT_FILE = STATE_DIR / "recording.output"

def start_recording():
    """Start screen recording using ffmpeg"""
    try:
        # Check if already recording
        if PID_FILE.exists():
            pid = int(PID_FILE.read_text().strip())
            # Check if process is still running
            try:
                os.kill(pid, 0)  # Check if process exists
                return {
                    "success": False,
                    "error": "Recording already in progress"
                }
            except OSError:
                # Process doesn't exist, clean up stale PID file
                PID_FILE.unlink()
                if OUTPUT_FILE.exists():
                    OUTPUT_FILE.unlink()

        # Create state directory
        STATE_DIR.mkdir(parents=True, exist_ok=True)

        # Create output directory
        output_dir = Path.home() / "Movies" / "SiC-Recordings"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_path = output_dir / f"sic-recording_{timestamp}.webm"

        # FFmpeg command for macOS screen recording
        command = [
            "ffmpeg",
            "-f", "avfoundation",
            "-i", "3:none",  # Capture screen 0 (device 3), no audio
            "-r", "30",  # 30 fps
            "-c:v", "libvpx-vp9",  # VP9 codec for WebM
            "-quality", "good",
            "-crf", "23",  # Quality
            "-b:v", "2M",  # Bitrate
            "-y",  # Overwrite output file
            str(output_path)
        ]

        # Start recording process
        process = subprocess.Popen(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        # Save PID and output path
        PID_FILE.write_text(str(process.pid))
        OUTPUT_FILE.write_text(str(output_path))

        return {
            "success": True,
            "message": "Recording started",
            "file_path": str(output_path)
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to start recording: {str(e)}"
        }

def stop_recording():
    """Stop screen recording"""
    try:
        # Check if recording PID file exists
        if not PID_FILE.exists():
            return {
                "success": False,
                "error": "No recording in progress"
            }

        # Read PID
        pid = int(PID_FILE.read_text().strip())

        # Read output path
        output_path = None
        if OUTPUT_FILE.exists():
            output_path = OUTPUT_FILE.read_text().strip()

        # Send SIGINT to gracefully stop ffmpeg
        try:
            os.kill(pid, signal.SIGINT)

            # Wait a bit for process to finish
            import time
            time.sleep(1)

            # Clean up state files
            PID_FILE.unlink()
            if OUTPUT_FILE.exists():
                OUTPUT_FILE.unlink()

            # Check if output file was created
            if output_path and os.path.exists(output_path):
                return {
                    "success": True,
                    "message": "Recording stopped",
                    "file_path": output_path
                }
            else:
                return {
                    "success": True,
                    "message": "Recording stopped (file may not be created yet)"
                }

        except ProcessLookupError:
            # Process already dead, clean up
            PID_FILE.unlink()
            if OUTPUT_FILE.exists():
                OUTPUT_FILE.unlink()
            return {
                "success": False,
                "error": "Recording process not found"
            }

    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to stop recording: {str(e)}"
        }

def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "success": False,
            "error": "Usage: screen_recorder.py [start|stop]"
        }))
        sys.exit(1)

    command = sys.argv[1]

    if command == "start":
        result = start_recording()
    elif command == "stop":
        result = stop_recording()
    else:
        result = {
            "success": False,
            "error": f"Unknown command: {command}"
        }

    # Output JSON result
    print(json.dumps(result))

if __name__ == "__main__":
    main()
