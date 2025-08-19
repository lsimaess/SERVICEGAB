import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app


def save_file(file_obj, subfolder='uploads'):
    """
    Save an uploaded file securely and return its relative path.
    """
    if not file_obj:
        return None

    # Generate a secure unique filename
    filename = secure_filename(file_obj.filename)
    ext = os.path.splitext(filename)[1]
    unique_name = f"{uuid.uuid4().hex}{ext}"

    # Define folder path
    folder_path = os.path.join(current_app.root_path, 'static', subfolder)
    os.makedirs(folder_path, exist_ok=True)

    # Save the file
    full_path = os.path.join(folder_path, unique_name)
    file_obj.save(full_path)

    # Return relative path (e.g., 'uploads/abc123.png')
    return f"{subfolder}/{unique_name}"


def delete_file(relative_path):
    """
    Delete a file from the filesystem using its relative path.
    """
    if not relative_path:
        return

    full_path = os.path.join(current_app.root_path, 'static', relative_path)
    if os.path.exists(full_path):
        os.remove(full_path)
