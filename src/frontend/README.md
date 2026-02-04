# Frontend API Contract

## GET `/api/machines-data/all`
Response:
```json
[
  {
    "name": "string",
    "status": "training | inference_on | inference_off",
    "lastInferenceResults": "number[] | null",
    "trainingProgress": "number | null"
  }
]
```

## POST `/api/model-train?name={machineName}`
Request:
```
Content-Type: text/csv
Body: <csv bytes>
```
Response: `200 OK`

## POST `/api/model-inference/start?name={machineName}`
Response: `200 OK`

## POST `/api/model-inference/stop?name={machineName}`
Response: `200 OK`
