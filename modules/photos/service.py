import os
import uuid
import asyncio
import logging
from typing import List, Tuple, Optional, Dict, Any
from datetime import datetime
from pathlib import Path
import json
from PIL import Image, ExifTags
from .models import PhotoInfo, PhotoConfig, PhotoMetadata
from .config import PhotoConfigManager

logger = logging.getLogger(__name__)

class PhotoService:
    """Photo service for managing family photos and slideshow."""
    
    def __init__(self):
        self.config_manager = PhotoConfigManager()
        self.config = self.config_manager.load_config()
        self.photos_db: Dict[str, PhotoInfo] = {}
        self.last_scan: Optional[datetime] = None
        
        # Ensure directories exist
        self._ensure_directories()
        
        # Load existing photo database (will be loaded on first request)
    
    def _ensure_directories(self):
        """Ensure photo and thumbnail directories exist."""
        try:
            os.makedirs(self.config.photos_directory, exist_ok=True)
            os.makedirs(self.config.thumbnails_directory, exist_ok=True)
            logger.info(f"Photo directories ready: {self.config.photos_directory}")
        except Exception as e:
            logger.error(f"Failed to create photo directories: {e}")
    
    async def _load_photo_database(self):
        """Load photo database from JSON file."""
        db_path = os.path.join(self.config.photos_directory, "photos.json")
        try:
            if os.path.exists(db_path):
                with open(db_path, 'r') as f:
                    data = json.load(f)
                    for photo_id, photo_data in data.items():
                        self.photos_db[photo_id] = PhotoInfo(**photo_data)
                logger.info(f"Loaded {len(self.photos_db)} photos from database")
            else:
                # Initialize with sample photos if directory has images
                await self.scan_directory()
        except Exception as e:
            logger.error(f"Failed to load photo database: {e}")
    
    async def _save_photo_database(self):
        """Save photo database to JSON file."""
        db_path = os.path.join(self.config.photos_directory, "photos.json")
        try:
            data = {photo_id: photo.dict() for photo_id, photo in self.photos_db.items()}
            with open(db_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save photo database: {e}")
    
    async def get_slideshow_photos(self, limit: int = 10) -> List[PhotoInfo]:
        """Get photos for slideshow display."""
        # Load database on first request if not loaded
        if not self.photos_db:
            await self._load_photo_database()
        
        if not self.photos_db:
            return self._get_demo_photos()
        
        photos = list(self.photos_db.values())
        
        # Filter for existing files
        valid_photos = []
        for photo in photos:
            if os.path.exists(photo.file_path):
                valid_photos.append(photo)
        
        # Sort by date taken or added date
        valid_photos.sort(key=lambda p: p.taken_date or p.added_date, reverse=True)
        
        return valid_photos[:limit]
    
    async def get_random_photo(self) -> PhotoInfo:
        """Get a random photo for display."""
        if not self.photos_db:
            return self._get_demo_photos()[0]
        
        import random
        valid_photos = [p for p in self.photos_db.values() if os.path.exists(p.file_path)]
        
        if not valid_photos:
            return self._get_demo_photos()[0]
        
        return random.choice(valid_photos)
    
    async def list_photos(self, offset: int = 0, limit: int = 20) -> Tuple[List[PhotoInfo], int]:
        """List photos with pagination."""
        if not self.photos_db:
            demo_photos = self._get_demo_photos()
            return demo_photos[offset:offset+limit], len(demo_photos)
        
        photos = list(self.photos_db.values())
        photos.sort(key=lambda p: p.added_date, reverse=True)
        
        total = len(photos)
        return photos[offset:offset+limit], total
    
    async def get_photo_path(self, photo_id: str, size: str = "medium") -> str:
        """Get photo file path by ID and size."""
        if photo_id not in self.photos_db:
            # Return demo photo for testing
            return self._get_demo_photo_path()
        
        photo = self.photos_db[photo_id]
        
        if size == "thumbnail" and photo.thumbnail_path:
            return photo.thumbnail_path
        else:
            return photo.file_path
    
    async def upload_photo(self, file) -> PhotoInfo:
        """Upload and process a new photo."""
        # Generate unique ID and filename
        photo_id = str(uuid.uuid4())
        file_extension = os.path.splitext(file.filename)[1].lower()
        new_filename = f"{photo_id}{file_extension}"
        file_path = os.path.join(self.config.photos_directory, new_filename)
        
        # Save uploaded file
        content = await file.read()
        with open(file_path, 'wb') as f:
            f.write(content)
        
        # Process photo
        photo_info = await self._process_photo(file_path, photo_id, file.filename)
        
        # Add to database
        self.photos_db[photo_id] = photo_info
        await self._save_photo_database()
        
        logger.info(f"Uploaded photo: {file.filename}")
        return photo_info
    
    async def delete_photo(self, photo_id: str):
        """Delete a photo and its files."""
        if photo_id not in self.photos_db:
            raise FileNotFoundError("Photo not found")
        
        photo = self.photos_db[photo_id]
        
        # Delete files
        if os.path.exists(photo.file_path):
            os.remove(photo.file_path)
        
        if photo.thumbnail_path and os.path.exists(photo.thumbnail_path):
            os.remove(photo.thumbnail_path)
        
        # Remove from database
        del self.photos_db[photo_id]
        await self._save_photo_database()
        
        logger.info(f"Deleted photo: {photo_id}")
    
    async def scan_directory(self) -> Tuple[int, int]:
        """Scan photo directory for new photos."""
        added = 0
        skipped = 0
        
        if not os.path.exists(self.config.photos_directory):
            return added, skipped
        
        for file_path in Path(self.config.photos_directory).glob("*"):
            if file_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
                # Check if already in database
                existing = any(p.file_path == str(file_path) for p in self.photos_db.values())
                
                if not existing:
                    try:
                        photo_id = str(uuid.uuid4())
                        photo_info = await self._process_photo(str(file_path), photo_id, file_path.name)
                        self.photos_db[photo_id] = photo_info
                        added += 1
                    except Exception as e:
                        logger.warning(f"Failed to process {file_path}: {e}")
                        skipped += 1
                else:
                    skipped += 1
        
        if added > 0:
            await self._save_photo_database()
        
        self.last_scan = datetime.now()
        logger.info(f"Photo scan complete: {added} added, {skipped} skipped")
        return added, skipped
    
    async def _process_photo(self, file_path: str, photo_id: str, original_filename: str) -> PhotoInfo:
        """Process a photo file and extract metadata."""
        try:
            with Image.open(file_path) as img:
                width, height = img.size
                format_name = img.format
                
                # Extract EXIF data
                metadata = self._extract_metadata(img)
                
                # Create thumbnail
                thumbnail_path = await self._create_thumbnail(file_path, photo_id)
                
                # Get file info
                stat = os.stat(file_path)
                file_size = stat.st_size
                
                return PhotoInfo(
                    id=photo_id,
                    filename=original_filename,
                    file_path=file_path,
                    thumbnail_path=thumbnail_path,
                    file_size=file_size,
                    width=width,
                    height=height,
                    format=format_name,
                    taken_date=metadata.get('taken_date'),
                    added_date=datetime.now(),
                    camera_info=metadata
                )
        except Exception as e:
            logger.error(f"Failed to process photo {file_path}: {e}")
            raise
    
    def _extract_metadata(self, img: Image.Image) -> Dict[str, Any]:
        """Extract metadata from image EXIF data."""
        metadata = {}
        
        try:
            exif = img._getexif()
            if exif:
                for tag_id, value in exif.items():
                    tag = ExifTags.TAGS.get(tag_id, tag_id)
                    
                    if tag == 'DateTime':
                        try:
                            metadata['taken_date'] = datetime.strptime(str(value), '%Y:%m:%d %H:%M:%S')
                        except:
                            pass
                    elif tag == 'Make':
                        metadata['camera_make'] = str(value)
                    elif tag == 'Model':
                        metadata['camera_model'] = str(value)
                    elif tag == 'FocalLength':
                        metadata['focal_length'] = float(value)
                    elif tag == 'FNumber':
                        metadata['aperture'] = f"f/{float(value)}"
                    elif tag == 'ISOSpeedRatings':
                        metadata['iso'] = int(value)
        except Exception as e:
            logger.debug(f"Could not extract EXIF data: {e}")
        
        return metadata
    
    async def _create_thumbnail(self, file_path: str, photo_id: str) -> str:
        """Create thumbnail for photo."""
        try:
            thumbnail_filename = f"{photo_id}_thumb.jpg"
            thumbnail_path = os.path.join(self.config.thumbnails_directory, thumbnail_filename)
            
            with Image.open(file_path) as img:
                img.thumbnail(self.config.thumbnail_size, Image.Resampling.LANCZOS)
                img.save(thumbnail_path, "JPEG", quality=85)
            
            return thumbnail_path
        except Exception as e:
            logger.warning(f"Failed to create thumbnail for {file_path}: {e}")
            return None
    
    def _get_demo_photos(self) -> List[PhotoInfo]:
        """Return demo photos for testing."""
        # Create demo images first
        demo_paths = []
        for i, (color, name) in enumerate([("lightblue", "family_photo"), ("lightgreen", "vacation")], 1):
            demo_path = f"/tmp/demo_photo_{i}.jpg"
            try:
                img = Image.new('RGB', (400, 300), color=color)
                img.save(demo_path, "JPEG")
                demo_paths.append(demo_path)
            except:
                demo_paths.append("/tmp/demo_photo.jpg")
        
        return [
            PhotoInfo(
                id="demo1",
                filename="family_photo.jpg",
                title="Family Photo",
                file_path=demo_paths[0] if len(demo_paths) > 0 else "/tmp/demo_photo.jpg",
                file_size=1024000,
                width=400,
                height=300,
                format="JPEG",
                added_date=datetime.now(),
                tags=["family", "demo"]
            ),
            PhotoInfo(
                id="demo2", 
                filename="vacation.jpg",
                title="Vacation Memory",
                file_path=demo_paths[1] if len(demo_paths) > 1 else "/tmp/demo_photo.jpg",
                file_size=2048000,
                width=400,
                height=300,
                format="JPEG",
                added_date=datetime.now(),
                tags=["vacation", "demo"]
            )
        ]
    
    def _get_demo_photo_path(self) -> str:
        """Return path to a demo photo."""
        # Create a simple demo image for testing
        demo_path = "/tmp/demo_photo.jpg"
        try:
            img = Image.new('RGB', (400, 300), color='lightblue')
            img.save(demo_path, "JPEG")
        except:
            pass
        return demo_path
    
    def get_config(self) -> PhotoConfig:
        """Get current photo configuration."""
        return self.config
    
    def update_config(self, new_config: PhotoConfig):
        """Update photo configuration."""
        self.config = new_config
        self.config_manager.save_config(new_config)
        self._ensure_directories()
        logger.info("Photo configuration updated")
    
    async def get_status(self) -> Dict[str, Any]:
        """Get photo service status."""
        return {
            "photos_count": len(self.photos_db),
            "photos_directory": self.config.photos_directory,
            "thumbnails_directory": self.config.thumbnails_directory,
            "last_scan": self.last_scan.isoformat() if self.last_scan else None,
            "auto_scan": self.config.auto_scan,
            "slideshow_interval": self.config.slideshow_interval,
            "directory_exists": os.path.exists(self.config.photos_directory),
            "total_size": sum(p.file_size for p in self.photos_db.values())
        }