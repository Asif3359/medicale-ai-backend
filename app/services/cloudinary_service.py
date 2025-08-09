import io
from typing import Optional, Tuple

import cloudinary
from cloudinary.uploader import upload as cloudinary_upload

from app.config import (
    CLOUDINARY_CLOUD_NAME,
    CLOUDINARY_API_KEY,
    CLOUDINARY_API_SECRET,
    CLOUDINARY_FOLDER,
)


def initialize_cloudinary() -> None:
    if not (CLOUDINARY_CLOUD_NAME and CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET):
        # Allow running without Cloudinary during local dev/tests; uploads will fail fast when called
        return
    cloudinary.config(
        cloud_name=CLOUDINARY_CLOUD_NAME,
        api_key=CLOUDINARY_API_KEY,
        api_secret=CLOUDINARY_API_SECRET,
        secure=True,
    )


def upload_image_bytes(image_bytes: bytes, filename: Optional[str] = None) -> Tuple[str, str]:
    """Upload image bytes to Cloudinary.

    Returns (secure_url, public_id).
    Raises Exception on failure.
    """
    initialize_cloudinary()

    upload_options = {
        "folder": CLOUDINARY_FOLDER,
        "resource_type": "image",
        "use_filename": True,
        "unique_filename": True,
        "overwrite": False,
    }
    if filename:
        upload_options["filename"] = filename

    result = cloudinary_upload(io.BytesIO(image_bytes), **upload_options)
    secure_url = result.get("secure_url")
    public_id = result.get("public_id")
    if not secure_url or not public_id:
        raise RuntimeError("Cloudinary upload did not return secure_url/public_id")
    return secure_url, public_id


