# Frontend API Contract

## GET `/api/machines-data/all`
Response:
```json
[
  {
    "name": "string",
    "status": "training | inference",
    "lastInferenceResults": "number[] | null",
    "trainingProgress": "number | null"
  }
]
```

## POST `/api/model-train/start?name={machineName}`
Request:
```
Content-Type: text/csv
Body: <csv bytes>
```
Response: `200 OK`

## GET `/api/inference-gateway/inference/active-inference-servers`
Response:
```json
[
  {
    "metadata": {
      "name": "atlas-01-inference-server",
      "annotations": {
        "model-name": "atlas-01"
      }
    }
  }
]
```

## POST `/api/inference-gateway/inference/create-server`
Request:
```json
{
  "model_name": "Atlas-01",
  "replicas": 1,
  "prediction_interval": 5
}
```
Response: `200 OK`

## POST `/api/inference-gateway/inference/delete-server`
Request:
```json
{
  "model_name": "Atlas-01"
}
```
Response: `200 OK`
