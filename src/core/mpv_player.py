import subprocess
import sys
import os
import socket
import json
import time

class MpvPlayer:
    def __init__(self):
        self.mpv_process = None
        self.socket_path = "/tmp/aniplay_mpv_socket"
        if os.path.exists(self.socket_path):
            os.remove(self.socket_path)

    def play_video(self, file_path):
        if not os.path.exists(file_path):
            print(f"Error: Video file not found at {file_path}")
            return

        if self.mpv_process and self.mpv_process.poll() is None:
            self.stop()
            time.sleep(0.1)

        mpv_command = [
            "mpv",
            f"--input-ipc-server={self.socket_path}",
            "--force-window",
            "--no-terminal",
            f"--title=AniPlay - {os.path.basename(file_path)}",
            file_path
        ]

        try:
            self.mpv_process = subprocess.Popen(mpv_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"Playing video: {file_path}")
        except FileNotFoundError:
            print("Error: MPV player not found. Please ensure 'mpv' is installed and in your system's PATH.")
        except Exception as e:
            print(f"An error occurred while trying to play video: {e}")

    def send_command(self, command):
        if not self.mpv_process or self.mpv_process.poll() is not None:
            print("MPV is not running.")
            return

        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
                sock.connect(self.socket_path)
                sock.sendall(json.dumps(command).encode('utf-8') + b'\n')
        except (ConnectionRefusedError, FileNotFoundError):
            print("Could not connect to MPV socket.")
        except Exception as e:
            print(f"Error sending command to MPV: {e}")

    def toggle_pause(self):
        self.send_command({"command": ["cycle", "pause"]})

    def stop(self):
        self.send_command({"command": ["quit"]})
        if self.mpv_process:
            try:
                self.mpv_process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.mpv_process.kill()
            self.mpv_process = None

    def __del__(self):
        if self.mpv_process and self.mpv_process.poll() is None:
            self.stop()
        if os.path.exists(self.socket_path):
            os.remove(self.socket_path)
