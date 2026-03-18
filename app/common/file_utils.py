import os
import uuid
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'app/static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_product_image(file):
    """Save uploaded image and return the URL"""
    if not file or file.filename == '':
        return None
    
    if not allowed_file(file.filename):
        raise ValueError("Invalid file type. Allowed: png, jpg, jpeg, gif, webp")
    
    # CHECK FILE SIZE
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        raise ValueError(f"File too large. Maximum size is {MAX_FILE_SIZE / (1024 * 1024):.0f}MB")
    
    if file_size == 0:
        raise ValueError("File is empty")
    
    # Create upload directory if it doesn't exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # Generate unique filename
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    
    # Save file directly without PIL processing
    file.save(filepath)
    
    # Return URL path
    return f"/static/uploads/{filename}"
