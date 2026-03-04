"""
File handling utilities
"""
import os
import uuid
from werkzeug.utils import secure_filename
from config import Config


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


def save_uploaded_file(file):
    """
    Save uploaded file to upload folder

    Returns:
        dict: File info with id, filename, path
    """
    if file is None:
        raise ValueError("No file provided")

    if not allowed_file(file.filename):
        raise ValueError(f"File type not allowed. Only {Config.ALLOWED_EXTENSIONS} are supported")

    # Generate unique filename
    file_id = str(uuid.uuid4())

    # Get extension from original filename before secure_filename processing
    # secure_filename may remove non-ASCII characters
    if '.' in file.filename:
        extension = file.filename.rsplit('.', 1)[1].lower()
    else:
        extension = 'docx'  # Default extension

    # Use secure_filename for the base name, or default if empty
    original_filename = secure_filename(file.filename)
    if not original_filename or '.' not in original_filename:
        # If secure_filename removed all characters, create a default name
        original_filename = f"uploaded_thesis.{extension}"

    saved_filename = f"{file_id}.{extension}"

    file_path = os.path.join(Config.UPLOAD_FOLDER, saved_filename)

    # Save file
    file.save(file_path)

    # Get file size
    file_size = os.path.getsize(file_path)

    return {
        'file_id': file_id,
        'filename': original_filename,
        'saved_filename': saved_filename,
        'file_path': file_path,
        'file_size': file_size,
        'extension': extension
    }


def get_file_path(file_id):
    """Get file path from file_id"""
    for ext in Config.ALLOWED_EXTENSIONS:
        file_path = os.path.join(Config.UPLOAD_FOLDER, f"{file_id}.{ext}")
        if os.path.exists(file_path):
            return file_path
    return None


def delete_file(file_id):
    """Delete file by file_id"""
    file_path = get_file_path(file_id)
    if file_path and os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False


def format_file_size(size_bytes):
    """Format file size to human readable format"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
