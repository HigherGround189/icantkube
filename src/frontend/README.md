## Frontend Model-Train PoC

This UI uploads a CSV directly to the model-train microservice and polls for results.

- **Start training**: `POST /api/model-train/start?filename=<originalFilename>`  
  - Body: raw file bytes (CSV), `Content-Type` set from the file or `application/octet-stream`.  
  - Client enforces a 25 MB limit before sending.  
  - Response expected: JSON `{ "trackingId": "<id>" }`.
- **Poll status**: `GET /api/model-train/status/<trackingId>`  
  - Response expected: JSON with at least `status` (`pending | running | completed | failed`).  
  - Optional fields: `progress` (number 0-100), `result` (any JSON serializable payload), `error` (string) for failures.

The UI keeps polling until status is `completed` or `failed`, then displays the `result` or `error`.
