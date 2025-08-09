import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "medical_ai_db")
MODEL_PATH = os.getenv("MODEL_PATH", "best_lung_disease_model.h5")
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# Auth
JWT_SECRET = os.getenv("JWT_SECRET", "change-me-in-prod")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# File storage (Cloudinary)
CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")
CLOUDINARY_FOLDER = os.getenv("CLOUDINARY_FOLDER", "medical-ai/uploads")

# Legacy local upload dir (unused when Cloudinary is configured, kept for backwards compat)
UPLOAD_DIR = os.getenv("UPLOAD_DIR", str(os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")))


