"""Compatibility shim. Use app.models.models instead."""
from app.models.models import (  # noqa: F401
    DiseaseClass,
    PredictionResult,
    User,
    PredictionRequest,
    PredictionResponse,
    UserStats,
)