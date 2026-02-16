## Model Train Service

Retrieve uploaded CSV from frontend to initate model training pipeline. Asynchronously return polls statuses and tracking of multiple training jobs. Each successful job stores model artifacts and metrics to MLFlow.

### Training upload & start (`/api/model-train`)
- `POST /api/model-train/start` (Call this to start a training job)
  - Fields: `filename` (string).
  - Behavior: Accepts sequential chunks; 
  - Backed responds `{ trackingId }` while initiating and running model training pipeline.
  - The frontend caps file size at 25 MB and sends chunks in order.
- `GET /api/model-train/status/:trackingId` → `{ status: pending|running|completed|failed, progress: number, result: any, error: string, modelId: string }`
  - When `status=completed`, include `modelId` (or `trainedModelId`) so inference can run.
- `GET /api/model-train/status` → `{ trackingId: string, status: pending|running|completed|failed }`
  - Allow checking of all available jobs tracking id with statuses.

### Model Pipeline Initiation
When a model training job is initiated, the service generate `trackingId` and creates an intial job status: `{ status: pending|running|completed|failed, progress: number, result: any, error: string }`. This job status is stored in Redis and used to queue the job for exection.

A celery worker `celery-app` will take on the queued job, runs the model training pipeline and continuously update the job status in Redis, where clients can poll the real-time status and progress. 

All trained artifacts (e.g. models, parameters, and evaluation metrics) are logged to MLflow. When training finishes successfully, the job status is updated to completed. If an error occurs, the status is set to failed and the error message is recorded.

### Model Inference Request
For inference, clients can retrieve a previously trained model from MLflow using the model registry reference (e.g. model name + version), then use it to generate predictions

Steps:
1. Select a model to serve (`models:/<model_name>/<version>`).
2. Load the model from MLflow into the inference service (`mlflow.pyfunc.load_model(<models:/...>)`).
3. Run predictions on input features and return the result to the client (`.predict(<input data>)`).

### Other (.py files)
> `connections.py`:
This module is responsible for initialising and managing external service connections used throughout the application.
Typical responsibilities include:
- Creating and reusing connections to services such as:
  1. Redis (broker / backend)
  2. Mariadb (database)
  3. RustFS (object storage)
  4. MLFlow
- Avoiding duplicated connection logic across Flask and Celery code

> `constants.py`:
This module stores shared constants and application-wide configuration values to ensure consistency.
Typical contents include:
- Status values (e.g. job states, progress)
- Default configuration values

This set up ensures Flask and Celery agree on the same values and makes code easier to read and refactor.

`logging.py`:
This module defines the centralised logging configuration for the entire application.
Typical responsibilities include:
- Configuring log format, log level, and handlers
- Ensuring consistent logs across:
  1. Flask API
  2. Celery workers
- Making logs compatible with containerized environments
