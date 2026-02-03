# Frontend API Contract

## GET `/machines-data/all`
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

## POST `/model-train?name={machineName}`
Request:
```
Content-Type: text/csv
Body: <csv bytes>
```
Response: `200 OK`

## POST `/model-inference/start?name={machineName}`
Response: `200 OK`

## POST `/model-inference/stop?name={machineName}`
Response: `200 OK`
