## Model Train Service

Retrieve uploaded CSV from frontend
The UI manages machines, uploads CSVs in 1 MB multipart chunks, starts model training, polls status, and runs inference. All requests are relative to the frontend origin.

### Machines (`/api/models`)
- `GET /api/models` → `{ machines: [{ id, name, imageUrl?, latestModelId?, latestModelStatus? }] }`
- `POST /api/models` with JSON `{ name, imageUrl? }` → `{ machine: { id, name, imageUrl } }`
- `DELETE /api/models/:id` → 204 on success

### Training upload & start (`/api/model-train`)
- `POST /api/model-train/chunk` (multipart/form-data)
  - Fields: `machineId` (string), `filename` (string), `chunkIndex` (int, 0-based), `isLast` ("true"/"false"), `chunk` (file slice, <= 1 MB), `uploadId` (string, optional after first response).
  - Behavior: accepts sequential chunks; responds `{ uploadId, status }` while receiving. On final chunk (`isLast=true`), backend should start training and respond `{ uploadId, trackingId, modelId? }`.
  - The frontend caps file size at 25 MB and sends chunks in order.
- `GET /api/model-train/status/:trackingId` → `{ status: pending|running|completed|failed, progress?: number, result?: any, error?: string, modelId?: string }`
  - When `status=completed`, include `modelId` (or `trainedModelId`) so inference can run.

### Inference (`/api/model-inference`)
- `POST /api/model-inference` with JSON `{ modelId, machineId, payload }` → arbitrary JSON inference result (rendered as-is).

### UI expectations
- On page load, `GET /api/models` populates machine cards. Latest model info (if provided) will show the inference box immediately.
- Upload flow: select CSV → UI sends 1 MB chunks with `isLast` flag; final response returns `trackingId` to poll status.
- Polling: every ~2s until `completed` or `failed`. Progress uses `progress` if provided.
- Inference box appears after training completes (when `modelId` is known). Payload is free-form text; adjust backend parsing as needed.

If the backend adds extra fields, the UI will ignore unknown fields but displays `result`, `error`, `progress`, `modelId`, and `status` when present.
