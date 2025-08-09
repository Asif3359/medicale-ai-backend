import numpy as np
import tensorflow as tf
from PIL import Image
import io
import time
from typing import Tuple, Dict
import os

from app.config import MODEL_PATH as DEFAULT_MODEL_PATH


class LungDiseasePredictor:
    """ML model service for lung disease prediction"""

    def __init__(self, model_path: str | None = None):
        self.model = None
        self.class_names = [
            "00 Anatomia Normal",
            "01 Processos Inflamatórios Pulmonares (Pneumonia)",
            "02 Maior Densidade (Derrame Pleural, Consolidação Atelectasica, Hidrotorax, Empiema)",
            "03 Menor Densidade (Pneumotorax, Pneumomediastino, Pneumoperitonio)",
            "04 Doenças Pulmonares Obstrutivas (Enfisema, Broncopneumonia, Bronquiectasia, Embolia)",
            "05 Doenças Infecciosas Degenerativas (Tuberculose, Sarcoidose, Proteinose, Fibrose)",
            "06 Lesões Encapsuladas (Abscessos, Nódulos, Cistos, Massas Tumorais, Metastases)",
            "07 Alterações de Mediastino (Pericardite, Malformações Arteriovenosas, Linfonodomegalias)",
            "08 Alterações do Tórax (Atelectasias, Malformações, Agenesia, Hipoplasias)",
        ]
        self.image_size = (128, 128)
        self.load_model(model_path or DEFAULT_MODEL_PATH)

    def load_model(self, model_path: str):
        """Load the trained model"""
        try:
            if os.path.exists(model_path):
                self.model = tf.keras.models.load_model(model_path)
                print(f"✅ Model loaded successfully from {model_path}")
            else:
                print(f"❌ Model file not found: {model_path}")
                print("Please ensure the model file exists or train the model first.")
        except Exception as e:
            print(f"❌ Error loading model: {e}")

    def preprocess_image(self, image_data: bytes) -> Tuple[np.ndarray, Tuple[int, int]]:
        """Preprocess uploaded image for prediction"""
        try:
            # Load image from bytes
            image = Image.open(io.BytesIO(image_data))
            original_size = image.size

            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')

            # Resize to model input size
            image = image.resize(self.image_size)

            # Convert to numpy array and normalize
            image_array = np.array(image)
            image_array = image_array.astype('float32') / 255.0

            # Add batch dimension
            image_array = np.expand_dims(image_array, axis=0)

            return image_array, original_size

        except Exception as e:
            raise ValueError(f"Error preprocessing image: {e}")

    def predict(self, image_data: bytes) -> Dict:
        """Make prediction on uploaded image"""
        if self.model is None:
            raise ValueError("Model not loaded. Please ensure the model file exists.")

        start_time = time.time()

        try:
            # Preprocess image
            processed_image, original_size = self.preprocess_image(image_data)

            # Make prediction
            predictions = self.model.predict(processed_image, verbose=0)

            # Get results
            predicted_class_idx = np.argmax(predictions[0])
            confidence_score = float(predictions[0][predicted_class_idx])
            predicted_class = self.class_names[predicted_class_idx]

            # Create all predictions dict
            all_predictions = {
                class_name: float(prob)
                for class_name, prob in zip(self.class_names, predictions[0])
            }

            processing_time = time.time() - start_time

            return {
                "predicted_class": predicted_class,
                "confidence_score": confidence_score,
                "all_predictions": all_predictions,
                "processing_time": processing_time,
                "original_size": original_size,
            }

        except Exception as e:
            raise ValueError(f"Error making prediction: {e}")

    def get_model_info(self) -> Dict:
        """Get model information"""
        return {
            "model_version": "1.0.0",
            "classes": self.class_names,
            "input_size": self.image_size,
            "total_classes": len(self.class_names),
        }


# Global predictor instance
predictor = LungDiseasePredictor()


