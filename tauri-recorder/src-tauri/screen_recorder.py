#!/usr/bin/env python3
"""
SiC Screen Recorder - Python Backend

Handles screen recording using ffmpeg on macOS.
"""

import sys
import json
import subprocess
import os
from datetime import datetime
from pathlib import Path

# Global process for recording
recording_process = None
output_file = None

def start_recording():
    """Start screen recording using ffmpeg"""
    global recording_process, output_file

    try:
        # Create output directory if it doesn't exist
        output_dir = Path.home() / "Movies" / "SiC-Recordings"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_file = output_dir / f"sic-recording_{timestamp}.webm"

        # FFmpeg command for macOS screen recording
        # Using avfoundation to capture screen
        command = [
            "ffmpeg",
            "-f", "avfoundation",
            "-i", "1:none",  # Capture display 1, no audio
            "-r", "30",  # 30 fps
            "-c:v", "libvpx-vp9",  # VP9 codec for WebM
            "-quality", "good",
            "-crf", "23",  # Quality (lower = better, 23 is good balance)
            "-b:v", "2M",  # Bitrate
            str(output_file)
        ]

        # Start recording process
        recording_process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        return {
            "success": True,
            "message": "Recording started",
            "file_path": str(output_file)
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to start recording: {str(e)}"
        }

def stop_recording():
    """Stop screen recording"""
    global recording_process, output_file

    try:
        if recording_process is None:
            return {
                "success": False,
                "error": "No recording in progress"
            }

        # Send SIGINT to gracefully stop ffmpeg
        recording_process.terminate()
        recording_process.wait(timeout=5)

        # Check if file was created
        if output_file and os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            return {
                "success": True,
                "message": "Recording stopped",
                "file_path": str(output_file)
            }
        else:
            return {
                "success": False,
                "error": "Recording file not found"
            }

    except subprocess.TimeoutExpired:
        # Force kill if graceful shutdown failed
        recording_process.kill()
        return {
            "success": False,
            "error": "Recording stopped forcefully (timeout)"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to stop recording: {str(e)}"
        }
    finally:
        recording_process = None
        output_file = None

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
