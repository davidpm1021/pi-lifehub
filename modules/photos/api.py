from fastapi import APIRouter, HTTPException, File, UploadFile
from fastapi.responses import FileResponse
from typing import Dict, Any, List
import logging
from .service import PhotoService
from .models import PhotoInfo, PhotoUploadResponse, PhotoConfig

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/photos", tags=["photos"])

# Initialize photo service
photo_service = PhotoService()

@router.get("/slideshow")
async def get_slideshow_photos(limit: int = 10) -> List[PhotoInfo]:
    """Get photos for slideshow display."""
    try:
        photos = await photo_service.get_slideshow_photos(limit)
        return photos
    except Exception as e:
        logger.error(f"Failed to get slideshow photos: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch photos")

@router.get("/random")
async def get_random_photo() -> PhotoInfo:
    """Get a random photo for display."""
    try:
        photo = await photo_service.get_random_photo()
        return photo
    except Exception as e:
        logger.error(f"Failed to get random photo: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch random photo")

@router.get("/list")
async def list_photos(offset: int = 0, limit: int = 20) -> Dict[str, Any]:
    """List all photos with pagination."""
    try:
        photos, total = await photo_service.list_photos(offset, limit)
        return {
            "photos": photos,
            "total": total,
            "offset": offset,
            "limit": limit
        }
    except Exception as e:
        logger.error(f"Failed to list photos: {e}")
        raise HTTPException(status_code=500, detail="Failed to list photos")

@router.get("/image/{photo_id}")
async def get_photo_image(photo_id: str, size: str = "medium"):
    """Get photo image file."""
    try:
        image_path = await photo_service.get_photo_path(photo_id, size)
        return FileResponse(image_path)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Photo not found")
    except Exception as e:
        logger.error(f"Failed to get photo image: {e}")
        raise HTTPException(status_code=500, detail="Failed to get photo image")

@router.post("/upload")
async def upload_photo(file: UploadFile = File(...)) -> PhotoUploadResponse:
    """Upload a new photo."""
    try:
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        photo_info = await photo_service.upload_photo(file)
        return PhotoUploadResponse(
            success=True,
            photo_id=photo_info.id,
            message="Photo uploaded successfully"
        )
    except Exception as e:
        logger.error(f"Failed to upload photo: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload photo")

@router.delete("/{photo_id}")
async def delete_photo(photo_id: str) -> Dict[str, str]:
    """Delete a photo."""
    try:
        await photo_service.delete_photo(photo_id)
        return {"status": "success", "message": "Photo deleted successfully"}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Photo not found")
    except Exception as e:
        logger.error(f"Failed to delete photo: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete photo")

@router.get("/config")
async def get_photo_config() -> PhotoConfig:
    """Get photo service configuration."""
    return photo_service.get_config()

@router.post("/config")
async def update_photo_config(config: PhotoConfig) -> Dict[str, str]:
    """Update photo service configuration."""
    try:
        photo_service.update_config(config)
        return {"status": "success", "message": "Photo configuration updated"}
    except Exception as e:
        logger.error(f"Failed to update photo config: {e}")
        raise HTTPException(status_code=500, detail="Failed to update configuration")

@router.post("/scan")
async def scan_photos() -> Dict[str, Any]:
    """Scan photo directory for new photos."""
    try:
        added, skipped = await photo_service.scan_directory()
        return {
            "status": "success",
            "photos_added": added,
            "photos_skipped": skipped,
            "message": f"Scan complete: {added} added, {skipped} skipped"
        }
    except Exception as e:
        logger.error(f"Failed to scan photos: {e}")
        raise HTTPException(status_code=500, detail="Failed to scan photos")

@router.get("/status")
async def get_photo_status() -> Dict[str, Any]:
    """Get photo service status."""
    try:
        status = await photo_service.get_status()
        return status
    except Exception as e:
        logger.error(f"Failed to get photo status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get photo status")