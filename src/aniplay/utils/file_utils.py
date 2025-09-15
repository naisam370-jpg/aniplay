#!/usr/bin/env python3
"""
File Utilities - Helper functions for file operations
File: src/aniplay/utils/file_utils.py
"""

import os
import re
import subprocess
import json
from typing import List, Optional
from pathlib import Path

# Common video file extensions
VIDEO_EXTENSIONS = {'.mp4', '.mkv', '.avi', '.mov', '.webm', '.m4v', '.flv', '.wmv', '.ogv', '.3gp'}

def get_video_files(directory: str, recursive: bool = False) -> List[str]:
    """
    Get all video files in a directory
    
    Args:
        directory: Directory to scan
        recursive: Whether to scan subdirectories
        
    Returns:
        List of video file paths
    """
    video_files = []
    
    if recursive:
        for root, dirs, files in os.walk(directory):
            for file in files:
                if is_video_file(file):
                    video_files.append(os.path.join(root, file))
    else:
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            if os.path.isfile(file_path) and is_video_file(file):
                video_files.append(file_path)
    
    return sorted(video_files, key=lambda x: natural_sort_key(os.path.basename(x)))

def is_video_file(filename: str) -> bool:
    """Check if a file is a video file based on extension"""
    _, ext = os.path.splitext(filename.lower())
    return ext in VIDEO_EXTENSIONS

def natural_sort_key(text: str) -> List:
    """
    Generate a key for natural sorting (handles numbers properly)
    Example: ['file1.mp4', 'file2.mp4', 'file10.mp4'] instead of ['file1.mp4', 'file10.mp4', 'file2.mp4']
    """
    def try_int(s):
        try:
            return int(s)
        except ValueError:
            return s.lower()
    
    return [try_int(c) for c in re.split(r'(\d+)', text)]

def get_video_duration(file_path: str, timeout: int = 30) -> int:
    """
    Get video duration in seconds using ffprobe
    
    Args:
        file_path: Path to video file
        timeout: Timeout in seconds
        
    Returns:
        Duration in seconds, 0 if unable to determine
    """
    try:
        result = subprocess.run([
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_format', file_path
        ], capture_output=True, text=True, timeout=timeout)
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            duration = float(data.get('format', {}).get('duration', 0))
            return int(duration)
            
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, 
            json.JSONDecodeError, ValueError, FileNotFoundError):
        pass
    
    return 0

def generate_video_thumbnail(video_path: str, thumbnail_path: str, 
                           timestamp: str = "00:00:10", 
                           width: int = 320, height: int = 180) -> bool:
    """
    Generate a thumbnail for a video file using ffmpeg
    
    Args:
        video_path: Path to source video
        thumbnail_path: Path where thumbnail will be saved
        timestamp: Time position for thumbnail (HH:MM:SS format)
        width: Thumbnail width
        height: Thumbnail height
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure thumbnail directory exists
        os.makedirs(os.path.dirname(thumbnail_path), exist_ok=True)
        
        # Generate thumbnail using ffmpeg
        result = subprocess.run([
            'ffmpeg', '-i', video_path, '-ss', timestamp,
            '-vframes', '1', '-vf', f'scale={width}:{height}',
            '-y', thumbnail_path  # -y to overwrite existing files
        ], capture_output=True, text=True, timeout=30)
        
        return result.returncode == 0 and os.path.exists(thumbnail_path)
        
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
        return False

def get_file_size(file_path: str) -> int:
    """Get file size in bytes"""
    try:
        return os.path.getsize(file_path)
    except (OSError, FileNotFoundError):
        return 0

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def format_duration(seconds: int) -> str:
    """Format duration in seconds to HH:MM:SS or MM:SS"""
    if seconds <= 0:
        return "0:00"
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes}:{secs:02d}"

def safe_filename(filename: str) -> str:
    """
    Convert a string to a safe filename by removing/replacing invalid characters
    """
    # Replace invalid characters with underscores
    invalid_chars = r'[<>:"/\\|?*]'
    safe_name = re.sub(invalid_chars, '_', filename)
    
    # Remove leading/trailing spaces and dots
    safe_name = safe_name.strip(' .')
    
    # Limit length
    if len(safe_name) > 255:
        safe_name = safe_name[:255]
    
    return safe_name

def ensure_directory(path: str) -> bool:
    """Ensure a directory exists, create if it doesn't"""
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except OSError:
        return False

def get_video_info(file_path: str) -> dict:
    """
    Get detailed video information using ffprobe
    
    Returns:
        Dict with video information: duration, width, height, codec, etc.
    """
    try:
        result = subprocess.run([
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_format', '-show_streams', file_path
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            
            # Extract format info
            format_info = data.get('format', {})
            duration = int(float(format_info.get('duration', 0)))
            size = int(format_info.get('size', 0))
            
            # Find video stream
            video_stream = None
            for stream in data.get('streams', []):
                if stream.get('codec_type') == 'video':
                    video_stream = stream
                    break
            
            info = {
                'duration': duration,
                'size': size,
                'format_name': format_info.get('format_name', 'unknown'),
            }
            
            if video_stream:
                info.update({
                    'width': video_stream.get('width', 0),
                    'height': video_stream.get('height', 0),
                    'codec': video_stream.get('codec_name', 'unknown'),
                    'fps': eval(video_stream.get('r_frame_rate', '0/1')) if video_stream.get('r_frame_rate') else 0
                })
            
            return info
            
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, 
            json.JSONDecodeError, ValueError, FileNotFoundError, ZeroDivisionError):
        pass
    
    return {
        'duration': 0,
        'size': 0,
        'width': 0,
        'height': 0,
        'codec': 'unknown',
        'format_name': 'unknown',
        'fps': 0
    }

def cleanup_old_files(directory: str, max_age_days: int = 30, pattern: str = "*") -> int:
    """
    Clean up old files in a directory
    
    Args:
        directory: Directory to clean
        max_age_days: Files older than this will be removed
        pattern: File pattern to match (glob style)
        
    Returns:
        Number of files removed
    """
    import time
    from glob import glob
    
    if not os.path.exists(directory):
        return 0
    
    current_time = time.time()
    max_age_seconds = max_age_days * 24 * 60 * 60
    removed_count = 0
    
    pattern_path = os.path.join(directory, pattern)
    
    for file_path in glob(pattern_path):
        try:
            if os.path.isfile(file_path):
                file_age = current_time - os.path.getmtime(file_path)
                if file_age > max_age_seconds:
                    os.remove(file_path)
                    removed_count += 1
        except OSError:
            continue
    
    return removed_count

def find_subtitle_files(video_path: str) -> List[str]:
    """
    Find subtitle files for a given video file
    
    Args:
        video_path: Path to video file
        
    Returns:
        List of subtitle file paths
    """
    subtitle_extensions = {'.srt', '.vtt', '.ass', '.ssa', '.sub', '.idx'}
    
    video_dir = os.path.dirname(video_path)
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    
    subtitle_files = []
    
    for file in os.listdir(video_dir):
        file_path = os.path.join(video_dir, file)
        if os.path.isfile(file_path):
            name, ext = os.path.splitext(file.lower())
            if ext in subtitle_extensions:
                # Check if subtitle file matches video name
                if name.startswith(video_name.lower()):
                    subtitle_files.append(file_path)
    
    return sorted(subtitle_files)

def get_directory_size(directory: str) -> int:
    """Get total size of all files in a directory (recursive)"""
    total_size = 0
    
    try:
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    total_size += os.path.getsize(file_path)
                except (OSError, FileNotFoundError):
                    continue
    except (OSError, FileNotFoundError):
        pass
    
    return total_size