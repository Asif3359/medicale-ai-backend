import os
import cloudinary
import cloudinary.uploader
from typing import Optional, Tuple
from app.config import (
    CLOUDINARY_CLOUD_NAME,
    CLOUDINARY_API_KEY,
    CLOUDINARY_API_SECRET,
    CLOUDINARY_FOLDER,
    UPLOAD_DIR,
)


class StorageService:
    """Handles file storage with Cloudinary in production, local files in development"""
    
    def __init__(self):
        self.use_cloudinary = bool(CLOUDINARY_CLOUD_NAME and CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET)
        
        if self.use_cloudinary:
            cloudinary.config(
                cloud_name=CLOUDINARY_CLOUD_NAME,
                api_key=CLOUDINARY_API_KEY,
                api_secret=CLOUDINARY_API_SECRET,
            )
            print(f"✅ Using Cloudinary storage (folder: {CLOUDINARY_FOLDER})")
        else:
            print(f"✅ Using local storage (directory: {UPLOAD_DIR})")
    
    async def upload_image(self, image_data: bytes, filename: str) -> Tuple[str, Optional[str]]:
        """
        Upload image and return (storage_path, cloudinary_url)
        
        Returns:
            - storage_path: filename for database storage
            - cloudinary_url: full URL if using Cloudinary, None if local
        """
        if self.use_cloudinary:
            return await self._upload_to_cloudinary(image_data, filename)
        else:
            return await self._save_locally(image_data, filename)
    
    async def _upload_to_cloudinary(self, image_data: bytes, filename: str) -> Tuple[str, str]:
        """Upload to Cloudinary and return (public_id, full_url)"""
        try:
            # Create unique public_id with timestamp
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
            public_id = f"{CLOUDINARY_FOLDER}/{timestamp}_{filename}"
            
            # Upload to Cloudinary
            result = cloudinary.uploader.upload(
                image_data,
                public_id=public_id,
                resource_type="image",
                overwrite=True
            )
            
            return public_id, result['secure_url']
            
        except Exception as e:
            print(f"❌ Cloudinary upload failed: {e}")
            # Fallback to local storage
            return await self._save_locally(image_data, filename)
    
    async def _save_locally(self, image_data: bytes, filename: str) -> Tuple[str, None]:
        """Save locally and return (filename, None)"""
        try:
            os.makedirs(UPLOAD_DIR, exist_ok=True)
            
            # Create unique filename with timestamp
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
            safe_filename = f"{timestamp}_{filename}"
            file_path = os.path.join(UPLOAD_DIR, safe_filename)
            
            with open(file_path, "wb") as f:
                f.write(image_data)
            
            return safe_filename, None
            
        except Exception as e:
            print(f"❌ Local file save failed: {e}")
            raise
    
    def get_image_url(self, storage_path: str, cloudinary_url: Optional[str] = None) -> str:
        """Get the full URL for an image"""
        if cloudinary_url:
            return cloudinary_url
        else:
            # For local files, return a relative path that can be served by FastAPI
            return f"/predictions/image/{storage_path}"
    
    def is_cloudinary_enabled(self) -> bool:
        """Check if Cloudinary is configured and enabled"""
        return self.use_cloudinary


# Global storage service instance
storage_service = StorageService()
