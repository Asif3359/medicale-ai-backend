# 🏥 Medical AI - Lung Disease Classification

A complete medical AI system for X-ray lung disease classification with web interface, MongoDB database, and REST API.

## 🚀 Features

- **AI-Powered Diagnosis**: 97% accurate lung disease classification
- **Interactive API Docs**: Swagger UI at `/docs` and ReDoc at `/redoc`
- **Database Storage**: MongoDB with Beanie ORM for prediction history
- **REST API**: Full API for integration with other systems
- **User Management**: Track user predictions and statistics
- **Real-time Analysis**: Instant X-ray analysis with confidence scores

## 📊 Model Performance

- **Accuracy**: 97.03%
- **F1 Score**: 97.01%
- **Classes**: 9 different lung disease categories
- **Processing Time**: < 1 second per image

## 🛠️ Technology Stack

- **Backend**: FastAPI, Python 3.12
- **Database**: MongoDB with Motor (async) and Beanie (ORM)
- **ML**: TensorFlow/Keras
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Deployment**: Docker-ready

## 📋 Prerequisites

1. **Python 3.12+**
2. **MongoDB** (local or cloud)
3. **Trained Model**: `best_lung_disease_model.h5`

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 2. Setup MongoDB

**Option A: Local MongoDB**
```bash
# Install MongoDB (Ubuntu/Debian)
sudo apt-get install mongodb

# Start MongoDB
sudo systemctl start mongodb
```

**Option B: MongoDB Atlas (Cloud)**
- Create account at [MongoDB Atlas](https://www.mongodb.com/atlas)
- Get connection string
- Update `.env` file

### 3. Environment Configuration

Create `.env` file:
```env
# Database
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=medical_ai_db

# Model
MODEL_PATH=best_lung_disease_model.h5

# Auth (change in production)
JWT_SECRET=change-me-in-prod
ACCESS_TOKEN_EXPIRE_MINUTES=60

# File storage
UPLOAD_DIR=uploads

# Server
HOST=0.0.0.0
PORT=8000
ENVIRONMENT=development
```

### 4. Run the Application

```bash
# Start the server
python main.py

# Or using uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. Access the Application

- **API Root (info)**: http://localhost:8000/
- **API Documentation (Swagger UI)**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📁 Project Structure

```
medicale-ai-backend/
├── app/
│   ├── main.py                     # FastAPI application (routes & startup)
│   ├── config.py                   # Environment configuration
│   ├── db/
│   │   └── database.py             # MongoDB (Motor) + Beanie initialization
│   ├── models/
│   │   └── models.py               # Beanie Documents + Pydantic schemas
│   └── services/
│       ├── ml_model.py             # ML predictor service
│       └── security.py             # Password hashing & JWT token
├── main.py                         # Thin launcher (imports app.main:app)
├── models.py                       # Back-compat shim → app/models/models.py
├── ml_model.py                     # Back-compat shim → app/services/ml_model.py
├── database.py                     # Back-compat shim → app/db/database.py
├── API_ENDPOINTS.md                # Detailed API reference
├── class9.py                       # Training script to generate the model .h5
├── static/                         # Static files (optional)
├── uploads/                        # Saved uploaded images
├── requirements.txt                # Python dependencies
└── best_lung_disease_model.h5      # Trained model (place here after training)
```

## 🔧 API Endpoints

See `API_ENDPOINTS.md` for full details. Key routes:

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/`                               | API info JSON |
| `POST` | `/predict`                        | Upload X-ray for analysis |
| `GET`  | `/predictions`                    | List predictions (optional `email`, `skip`, `limit`) |
| `GET`  | `/user/{email}/predictions`       | List predictions for a user |
| `GET`  | `/predictions/{id}/image`         | Download uploaded image for a prediction |
| `GET`  | `/health`                         | System health check |
| `GET`  | `/stats`                          | System statistics |
| `GET`  | `/user/{email}/stats`             | User statistics |
| `POST` | `/auth/register`                  | Register user, returns JWT |
| `POST` | `/auth/login`                     | Login user, returns JWT |

### Example API Usage

```bash
# Upload X-ray image
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@xray.jpg" \
  -F "user_name=John Doe" \
  -F "user_email=john@example.com"

# Get system stats
curl "http://localhost:8000/stats"

# List predictions (latest 50)
curl "http://localhost:8000/predictions"

# List predictions for a user
curl "http://localhost:8000/user/john@example.com/predictions?limit=10"

# Register user
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"name":"John Doe","email":"john@example.com","password":"Secret123!"}'

# Login user
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"john@example.com","password":"Secret123!"}'
```

## 🧠 Train the model (optional)

Use `class9.py` to train and generate `best_lung_disease_model.h5`.

```bash
cd /home/asif-ahammed/Documents/medical-ai/medicale-ai-backend
source venv/bin/activate  # if not already active
python class9.py
```

Outputs:
- `best_lung_disease_model.h5` (at project root)
- `training_history.png`, `confusion_matrix.png`

Notes:
- The script downloads the dataset via KaggleHub; ensure internet access and sufficient disk space.
- If you place the model elsewhere, set `MODEL_PATH` in `.env` accordingly.

## 🏥 Disease Classes

The model can classify 9 different lung conditions:

1. 00 Anatomia Normal
2. 01 Processos Inflamatórios Pulmonares (Pneumonia)
3. 02 Maior Densidade (Derrame Pleural, Consolidação Atelectasica, Hidrotorax, Empiema)
4. 03 Menor Densidade (Pneumotorax, Pneumomediastino, Pneumoperitonio)
5. 04 Doenças Pulmonares Obstrutivas (Enfisema, Broncopneumonia, Bronquiectasia, Embolia)
6. 05 Doenças Infecciosas Degenerativas (Tuberculose, Sarcoidose, Proteinose, Fibrose)
7. 06 Lesões Encapsuladas (Abscessos, Nódulos, Cistos, Massas Tumorais, Metastases)
8. 07 Alterações de Mediastino (Pericardite, Malformações Arteriovenosas, Linfonodomegalias)
9. 08 Alterações do Tórax (Atelectasias, Malformações, Agenesia, Hipoplasias)

## 🎯 Usage Instructions

### Web Interface

1. **Open**: Navigate to http://localhost:8000
2. **Upload**: Drag & drop or click to upload X-ray image
3. **Optional**: Enter name and email for tracking
4. **Analyze**: Click "Analyze X-ray" button
5. **Results**: View prediction with confidence score

### API Integration

```python
import requests

# Upload image for analysis
with open('xray.jpg', 'rb') as f:
    files = {'file': f}
    data = {
        'user_name': 'John Doe',
        'user_email': 'john@example.com'
    }
    response = requests.post('http://localhost:8000/predict', 
                           files=files, data=data)
    
    result = response.json()
    print(f"Prediction: {result['predicted_class']}")
    print(f"Confidence: {result['confidence_score']:.2%}")
```

## 🗄️ Database Schema

### PredictionResult Collection
```json
{
  "_id": "ObjectId",
  "created_at": "datetime",
  "user_name": "string",
  "user_email": "string",
  "image_filename": "string",
  "image_size": [width, height],
  "predicted_class": "enum",
  "confidence_score": "float",
  "all_predictions": {"class": "probability"},
  "processing_time": "float",
  "model_version": "string"
}
```

### User Collection
```json
{
  "_id": "ObjectId",
  "created_at": "datetime",
  "name": "string",
  "email": "string",
  "total_predictions": "integer"
}
```

## 🔒 Security Considerations

- **Input Validation**: All uploaded files are validated
- **Error Handling**: Comprehensive error handling
- **Authentication**: JWT helpers and auth endpoints provided; protect sensitive routes in production
- **Rate Limiting**: Consider implementing rate limiting for production
- **HTTPS**: Use HTTPS in production

Note: Uploaded images are stored in `uploads/`. Ensure proper storage policies in production.

## 🚀 Deployment

### Docker Deployment

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "main.py"]
```

### Production Checklist

- [ ] Set up MongoDB with authentication
- [ ] Configure environment variables
- [ ] Set up HTTPS/SSL
- [ ] Implement rate limiting
- [ ] Add monitoring and logging
- [ ] Set up backup strategy
- [ ] Configure load balancing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the API documentation at `/docs`
- Review the health check at `/health`

## 🏆 Acknowledgments

- Dataset: [Kaggle X-ray Lung Diseases](https://www.kaggle.com/datasets/fernando2rad/x-ray-lung-diseases-images-9-classes)
- Framework: FastAPI, TensorFlow, MongoDB
- UI: Bootstrap 5, Font Awesome

---

**⚠️ Medical Disclaimer**: This system is for educational and research purposes only. Always consult with qualified medical professionals for actual medical diagnosis. 