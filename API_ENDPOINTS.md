## API Endpoints

Base URL: `http://localhost:8000`

### GET `/`
- Returns API info JSON: `{ name, version, endpoints }`.

### POST `/predict`
- Content-Type: `multipart/form-data`
- Fields:
  - `file` (required): image file
  - `user_name` (optional): string
  - `user_email` (optional): string
- Responses:
  - 200: `{ prediction_id, predicted_class, confidence_score, all_predictions, processing_time, created_at }`
  - 400: invalid file
  - 500: prediction error

### GET `/predictions`
- Query params:
  - `skip` (int, default 0): pagination offset
  - `limit` (int, default 50, max 100): number of items
  - `email` (string, optional): filter by user email
- 200: `[{ prediction_id, predicted_class, confidence_score, all_predictions, processing_time, created_at }]`

### GET `/user/{email}/predictions`
- Query params:
  - `skip` (int, default 0): pagination offset
  - `limit` (int, default 50, max 100): number of items
- 200: `[{ prediction_id, predicted_class, confidence_score, all_predictions, processing_time, created_at }]`

### GET `/predictions/{prediction_id}/image`
- Returns the uploaded image file for the given prediction if available.
- 200: image file
- 404: not found

### GET `/health`
- 200: `{ status, database, model, timestamp }`

### GET `/stats`
- 200: `{ total_predictions, recent_predictions, model_info }`

### GET `/user/{email}/stats`
- 200: `{ total_predictions, most_common_prediction, average_confidence }`
- 404: user not found

### POST `/auth/register`
- Content-Type: `application/json`
- Body:
  - `name`: string
  - `email`: string
  - `password`: string
- Responses:
  - 200: `{ access_token, token_type }`
  - 400: email already registered

### POST `/auth/login`
- Content-Type: `application/json`
- Body:
  - `email`: string
  - `password`: string
- Responses:
  - 200: `{ access_token, token_type }`
  - 401: invalid credentials
  - 403: user inactive

### Docs
- GET `/docs` (Swagger UI)
- GET `/redoc`
- GET `/openapi.json`


