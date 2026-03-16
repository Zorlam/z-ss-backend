import os
import uuid
from werkzeug.utils import secure_filename
from PIL import Image

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
    
    # CHECK FILE SIZE - NEW SECURITY CHECK
    file.seek(0, os.SEEK_END)  # Go to end of file
    file_size = file.tell()  # Get position (= file size)
    file.seek(0)  # Reset to beginning
    
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
    
    # ADDITIONAL SECURITY: Verify it's actually an image by opening it
    try:
        image = Image.open(file)
        image.verify()  # Verify it's a valid image
        file.seek(0)  # Reset after verify
        image = Image.open(file)  # Reopen for processing
    except Exception:
        raise ValueError("Invalid or corrupted image file")
    
    # Resize if too large (max 1200x1200)
    if image.width > 1200 or image.height > 1200:
        image.thumbnail((1200, 1200), Image.Resampling.LANCZOS)
    
    # Convert RGBA to RGB if needed
    if image.mode == 'RGBA':
        background = Image.new('RGB', image.size, (255, 255, 255))
        background.paste(image, mask=image.split()[3])
        image = background
    
    # Save optimized image
    image.save(filepath, optimize=True, quality=85)
    
    # Return URL path
    return f"/static/uploads/{filename}"