from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import Optional
from pathlib import Path

from app.db.database import db
from app.services.ml_model import predictor
from app.services.security import hash_password, verify_password, create_access_token
from app.models.models import (
    PredictionResult,
    User,
    PredictionResponse,
    UserStats,
    DiseaseClass,
    UserCreate,
    UserLogin,
    TokenResponse,
)
from app.config import UPLOAD_DIR
import os
from bson import ObjectId


app = FastAPI(
    title="Medical AI - Lung Disease Classification",
    description="AI-powered X-ray lung disease classification system",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    await db.connect()


@app.on_event("shutdown")
async def shutdown_event():
    await db.disconnect()


@app.get("/")
async def read_root():
    return {
        "name": "Medical AI - Lung Disease Classification API",
        "version": "1.0.0",
        "endpoints": [
            "/predict",
            "/predictions",
            "/user/{email}/predictions",
            "/health",
            "/stats",
            "/user/{email}/stats",
            "/auth/register",
            "/auth/login",
        ],
    }


@app.post("/predict", response_model=PredictionResponse)
async def predict_disease(
    file: UploadFile = File(...),
    user_name: str | None = Form(None),
    user_email: str | None = Form(None),
):
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")

    try:
        image_data = await file.read()
        prediction_result = predictor.predict(image_data)

        # Normalize empty strings to None
        user_name = user_name or None
        user_email = user_email or None

        # Optionally persist uploaded image for preview
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        saved_path = None
        if file and file.filename:
            # Prefix with timestamp to avoid collisions
            from datetime import datetime as _dt
            safe_name = f"{_dt.now().strftime('%Y%m%d%H%M%S%f')}_{file.filename}"
            saved_path = os.path.join(UPLOAD_DIR, safe_name)
            with open(saved_path, "wb") as f:
                f.write(image_data)

        prediction_record = PredictionResult(
            user_name=user_name,
            user_email=user_email,
            image_filename=os.path.basename(saved_path) if saved_path else file.filename,
            image_size=prediction_result["original_size"],
            predicted_class=DiseaseClass(prediction_result["predicted_class"]),
            confidence_score=prediction_result["confidence_score"],
            all_predictions=prediction_result["all_predictions"],
            processing_time=prediction_result["processing_time"],
        )

        await prediction_record.insert()

        if user_email:
            user = await User.find_one({"email": user_email})
            if user:
                user.total_predictions += 1
                await user.save()
            else:
                user = User(name=user_name or "Anonymous", email=user_email)
                await user.insert()

        prediction_id = str(prediction_record.id) if prediction_record.id else None

        return PredictionResponse(
            prediction_id=prediction_id,
            predicted_class=prediction_result["predicted_class"],
            confidence_score=prediction_result["confidence_score"],
            all_predictions=prediction_result["all_predictions"],
            processing_time=prediction_result["processing_time"],
            created_at=prediction_record.created_at,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


@app.get("/predictions", response_model=list[PredictionResponse])
async def list_predictions(
    skip: int = 0,
    limit: int = 50,
    email: Optional[str] = None,
):
    """List predictions, newest first. Optional filter by user email.

    Query params:
    - skip: offset for pagination
    - limit: number of items to return (max 100)
    - email: filter by user_email
    """
    if limit > 100:
        limit = 100

    query = {"user_email": email} if email else {}
    items = (
        await PredictionResult.find(query)
        .sort([("created_at", -1)])
        .skip(skip)
        .limit(limit)
        .to_list()
    )

    return [
        PredictionResponse(
            prediction_id=str(p.id) if p.id else None,
            predicted_class=p.predicted_class.value if hasattr(p.predicted_class, "value") else str(p.predicted_class),
            confidence_score=p.confidence_score,
            all_predictions=p.all_predictions,
            processing_time=p.processing_time,
            created_at=p.created_at,
        )
        for p in items
    ]


@app.get("/user/{email}/predictions", response_model=list[PredictionResponse])
async def list_predictions_by_email(email: str, skip: int = 0, limit: int = 50):
    if limit > 100:
        limit = 100

    items = (
        await PredictionResult.find({"user_email": email})
        .sort([("created_at", -1)])
        .skip(skip)
        .limit(limit)
        .to_list()
    )

    return [
        PredictionResponse(
            prediction_id=str(p.id) if p.id else None,
            predicted_class=p.predicted_class.value if hasattr(p.predicted_class, "value") else str(p.predicted_class),
            confidence_score=p.confidence_score,
            all_predictions=p.all_predictions,
            processing_time=p.processing_time,
            created_at=p.created_at,
        )
        for p in items
    ]


@app.get("/predictions/{prediction_id}/image")
async def get_prediction_image(prediction_id: str):
    """Return the uploaded image file for a given prediction id if available."""
    try:
        obj_id = ObjectId(prediction_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid prediction id")

    pred = await PredictionResult.get(obj_id)
    if not pred or not pred.image_filename:
        raise HTTPException(status_code=404, detail="Image not found")

    path = os.path.join(UPLOAD_DIR, pred.image_filename)
    if not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="Image file missing")

    return FileResponse(path)


@app.get("/health")
async def health_check():
    db_health = await db.health_check()
    model_info = predictor.get_model_info()

    return {
        "status": "healthy",
        "database": db_health,
        "model": model_info,
        "timestamp": datetime.now(),
    }


@app.get("/stats")
async def get_stats():
    try:
        total_predictions = await PredictionResult.count()
        recent_predictions = (
            await PredictionResult.find().sort([("created_at", -1)]).limit(10).to_list()
        )

        return {
            "total_predictions": total_predictions,
            "recent_predictions": recent_predictions,
            "model_info": predictor.get_model_info(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")


@app.get("/user/{email}/stats")
async def get_user_stats(email: str):
    try:
        user = await User.find_one({"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        predictions = await PredictionResult.find({"user_email": email}).to_list()

        if not predictions:
            return UserStats(
                total_predictions=0,
                average_confidence=0.0,
            )

        total_predictions = len(predictions)
        average_confidence = sum(p.confidence_score for p in predictions) / total_predictions

        prediction_counts: dict[str, int] = {}
        for pred in predictions:
            pred_class = pred.predicted_class.value
            prediction_counts[pred_class] = prediction_counts.get(pred_class, 0) + 1

        most_common = max(prediction_counts.items(), key=lambda x: x[1])[0] if prediction_counts else None

        return UserStats(
            total_predictions=total_predictions,
            most_common_prediction=most_common,
            average_confidence=average_confidence,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting user stats: {str(e)}")


@app.post("/auth/register", response_model=TokenResponse)
async def register_user(payload: UserCreate):
    existing = await User.find_one({"email": payload.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        name=payload.name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
    )
    await user.insert()

    token = create_access_token(subject=str(user.id), extra_claims={"email": user.email})
    return TokenResponse(access_token=token)


@app.post("/auth/login", response_model=TokenResponse)
async def login_user(payload: UserLogin):
    user = await User.find_one({"email": payload.email})
    if not user or not user.hashed_password or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="User is inactive")

    token = create_access_token(subject=str(user.id), extra_claims={"email": user.email})
    return TokenResponse(access_token=token)

