from datetime import datetime
from typing import Optional
from beanie import Document
from pydantic import BaseModel, Field
from enum import Enum
from bson import ObjectId


class DiseaseClass(str, Enum):
    NORMAL = "00 Anatomia Normal"
    PNEUMONIA = "01 Processos Inflamatórios Pulmonares (Pneumonia)"
    HIGH_DENSITY = "02 Maior Densidade (Derrame Pleural, Consolidação Atelectasica, Hidrotorax, Empiema)"
    LOW_DENSITY = "03 Menor Densidade (Pneumotorax, Pneumomediastino, Pneumoperitonio)"
    OBSTRUCTIVE = "04 Doenças Pulmonares Obstrutivas (Enfisema, Broncopneumonia, Bronquiectasia, Embolia)"
    INFECTIOUS = "05 Doenças Infecciosas Degenerativas (Tuberculose, Sarcoidose, Proteinose, Fibrose)"
    ENCAPSULATED = "06 Lesões Encapsuladas (Abscessos, Nódulos, Cistos, Massas Tumorais, Metastases)"
    MEDIASTINUM = "07 Alterações de Mediastino (Pericardite, Malformações Arteriovenosas, Linfonodomegalias)"
    THORAX = "08 Alterações do Tórax (Atelectasias, Malformações, Agenesia, Hipoplasias)"


class PredictionResult(Document):
    """Database model for storing prediction results"""

    # Basic info
    id: Optional[ObjectId] = Field(default_factory=ObjectId, alias="_id")
    created_at: datetime = datetime.now()

    class Settings:
        name = "predictions"
        indexes = [
            "created_at",
            "predicted_class",
            "user_email",
        ]

    class Config:
        arbitrary_types_allowed = True

    # User info
    user_name: Optional[str] = None
    user_email: Optional[str] = None

    # Image info
    image_filename: Optional[str] = None
    image_url: Optional[str] = None
    image_size: tuple[int, int]

    # Prediction results
    predicted_class: DiseaseClass
    confidence_score: float
    all_predictions: dict[str, float]  # All class probabilities

    # Additional metadata
    processing_time: float  # seconds
    model_version: str = "1.0.0"

    class Settings:
        name = "predictions"
        indexes = [
            "created_at",
            "predicted_class",
            "user_email",
        ]


class User(Document):
    """Database model for storing user information and credentials"""

    id: Optional[ObjectId] = Field(default_factory=ObjectId, alias="_id")
    created_at: datetime = datetime.now()

    class Settings:
        name = "users"
        indexes = [
            "email",
        ]

    class Config:
        arbitrary_types_allowed = True

    # Profile
    name: str
    email: str
    total_predictions: int = 0

    # Auth
    hashed_password: str | None = None
    is_active: bool = True
    is_admin: bool = False


# Pydantic models for API requests/responses
class PredictionRequest(BaseModel):
    user_name: Optional[str] = None
    user_email: Optional[str] = None


class PredictionResponse(BaseModel):
    prediction_id: str
    predicted_class: str
    confidence_score: float
    all_predictions: dict[str, float]
    processing_time: float
    created_at: datetime
    image_url: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str,
        }


class UserStats(BaseModel):
    total_predictions: int
    most_common_prediction: Optional[str] = None
    average_confidence: float


class UserCreate(BaseModel):
    name: str
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


