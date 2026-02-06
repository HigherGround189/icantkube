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
