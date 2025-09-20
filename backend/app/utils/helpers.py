import os
import hashlib
import uuid
from typing import Optional
import logging

logger = logging.getLogger(__name__)

def generate_unique_filename(original_filename: str) -> str:
    """Generate a unique filename while preserving extension"""
    try:
        file_ext = os.path.splitext(original_filename)[1]
        unique_id = str(uuid.uuid4())
        return f"{unique_id}{file_ext}"
    except Exception as e:
        logger.error(f"Error generating unique filename: {e}")
        return f"{uuid.uuid4()}.jpg"

def calculate_file_hash(file_content: bytes) -> str:
    """Calculate SHA-256 hash of file content"""
    try:
        return hashlib.sha256(file_content).hexdigest()
    except Exception as e:
        logger.error(f"Error calculating file hash: {e}")
        return ""

def validate_image_file(file_content: bytes, max_size: int = 10 * 1024 * 1024) -> bool:
    """Validate image file content"""
    try:
        # Check file size
        if len(file_content) > max_size:
            return False
        
        # Check for valid image headers
        valid_headers = [
            b'\xff\xd8\xff',  # JPEG
            b'\x89PNG\r\n\x1a\n',  # PNG
            b'BM',  # BMP
            b'II*\x00',  # TIFF
            b'MM\x00*'  # TIFF
        ]
        
        for header in valid_headers:
            if file_content.startswith(header):
                return True
        
        return False
        
    except Exception as e:
        logger.error(f"Error validating image file: {e}")
        return False

def create_directory_if_not_exists(directory_path: str) -> bool:
    """Create directory if it doesn't exist"""
    try:
        os.makedirs(directory_path, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Error creating directory {directory_path}: {e}")
        return False

def safe_file_operation(operation, *args, **kwargs):
    """Safely perform file operations with error handling"""
    try:
        return operation(*args, **kwargs)
    except Exception as e:
        logger.error(f"File operation failed: {e}")
        return None

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    try:
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    except Exception as e:
        logger.error(f"Error formatting file size: {e}")
        return "Unknown"

def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing dangerous characters"""
    try:
        # Remove or replace dangerous characters
        dangerous_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        sanitized = filename
        
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '_')
        
        # Remove leading/trailing spaces and dots
        sanitized = sanitized.strip(' .')
        
        # Ensure filename is not empty
        if not sanitized:
            sanitized = "unnamed_file"
        
        return sanitized
    except Exception as e:
        logger.error(f"Error sanitizing filename: {e}")
        return "unnamed_file"

def get_file_extension(filename: str) -> str:
    """Get file extension in lowercase"""
    try:
        return os.path.splitext(filename)[1].lower()
    except Exception as e:
        logger.error(f"Error getting file extension: {e}")
        return ""

def is_allowed_file_type(filename: str, allowed_extensions: set) -> bool:
    """Check if file type is allowed"""
    try:
        file_ext = get_file_extension(filename)
        return file_ext in allowed_extensions
    except Exception as e:
        logger.error(f"Error checking file type: {e}")
        return False
