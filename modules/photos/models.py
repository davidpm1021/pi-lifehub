from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class PhotoInfo(BaseModel):
    """Photo information model."""
    id: str
    filename: str
    title: Optional[str] = None
    description: Optional[str] = None
    file_path: str
    thumbnail_path: Optional[str] = None
    file_size: int  # bytes
    width: int
    height: int
    format: str  # JPEG, PNG, etc.
    taken_date: Optional[datetime] = None
    added_date: datetime
    tags: List[str] = []
    people: List[str] = []
    location: Optional[str] = None
    camera_info: Optional[Dict[str, Any]] = None

class PhotoUploadResponse(BaseModel):
    """Response for photo upload."""
    success: bool
    photo_id: str
    message: str
    error: Optional[str] = None

class PhotoConfig(BaseModel):
    """Photo service configuration."""
    photos_directory: str = "/home/pi/Photos"
    thumbnails_directory: str = "/home/pi/Photos/thumbnails" 
    slideshow_interval: int = 10  # seconds
    max_photo_size: int = 10 * 1024 * 1024  # 10MB
    allowed_formats: List[str] = ["JPEG", "JPG", "PNG", "GIF", "BMP"]
    thumbnail_size: tuple = (200, 200)
    auto_scan: bool = True
    scan_interval: int = 3600  # seconds (1 hour)
    show_metadata: bool = True
    shuffle_slideshow: bool = True

class PhotoMetadata(BaseModel):
    """Photo metadata extracted from EXIF."""
    camera_make: Optional[str] = None
    camera_model: Optional[str] = None
    lens_info: Optional[str] = None
    focal_length: Optional[float] = None
    aperture: Optional[str] = None
    shutter_speed: Optional[str] = None
    iso: Optional[int] = None
    flash: Optional[bool] = None
    gps_latitude: Optional[float] = None
    gps_longitude: Optional[float] = None
    orientation: Optional[int] = None

class PhotoFilter(BaseModel):
    """Photo filtering options."""
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    tags: List[str] = []
    people: List[str] = []
    location: Optional[str] = None
    format: Optional[str] = None
    min_width: Optional[int] = None
    min_height: Optional[int] = None

class SlideshowConfig(BaseModel):
    """Slideshow-specific configuration."""
    enabled: bool = True
    interval: int = 10  # seconds
    transition_effect: str = "fade"  # fade, slide, none
    show_filename: bool = False
    show_date: bool = True
    show_location: bool = False
    random_order: bool = True
    include_subdirectories: bool = True