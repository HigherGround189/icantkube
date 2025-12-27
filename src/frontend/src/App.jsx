import { useEffect, useRef, useState } from "react";

const MAX_FILE_SIZE = 25 * 1024 * 1024; // 25 MB
const POLL_INTERVAL_MS = 1500;

export default function App() {
  const [file, setFile] = useState(null);
  const [trackingId, setTrackingId] = useState("");
  const [status, setStatus] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [polling, setPolling] = useState(false);

  const pollTimeout = useRef(null);
  const abortRef = useRef(null);

  useEffect(() => {
    return () => {
      if (pollTimeout.current) clearTimeout(pollTimeout.current);
      if (abortRef.current) abortRef.current.abort();
    };
  }, []);

  const onFileChange = (event) => {
    const selected = event.target.files?.[0];
    setError("");
    setResult(null);
    setTrackingId("");
    setStatus("");

    if (!selected) {
      setFile(null);
      return;
    }

    if (selected.size > MAX_FILE_SIZE) {
      setError("File is larger than 25 MB limit.");
      setFile(null);
      return;
    }

    setFile(selected);
  };

  async function startTraining() {
    if (!file) {
      setError("Choose a CSV file first.");
      return;
    }

    setError("");
    setResult(null);
    setStatus("Uploading and starting training...");

    const url = `/api/model-train/start?filename=${encodeURIComponent(file.name)}`;

    try {
      const res = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": file.type || "application/octet-stream",
        },
        body: file,
      });

      if (!res.ok) {
        const message = await res.text();
        throw new Error(message || "Failed to start training");
      }

      const data = await res.json();
      if (!data.trackingId) throw new Error("No trackingId returned from backend");

      setTrackingId(data.trackingId);
      setPolling(true);
      setStatus("Training started. Polling for status...");
    } catch (err) {
      setError(err.message || "Unexpected error");
      setStatus("");
      setPolling(false);
    }
  }

  async function pollStatus(id) {
    if (abortRef.current) abortRef.current.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    try {
      const res = await fetch(`/api/model-train/status/${id}`, { signal: controller.signal });
      if (!res.ok) {
        const message = await res.text();
        throw new Error(message || "Failed to fetch status");
      }

      const data = await res.json();
      const state = data.status || "unknown";
      setStatus(`Status: ${state}${data.progress != null ? ` (${data.progress}%)` : ""}`);

      if (state === "completed") {
        setResult(data.result ?? "Training completed (no result payload)");
        setPolling(false);
        return;
      }

      if (state === "failed") {
        setError(data.error || "Training failed");
        setPolling(false);
        return;
      }

      pollTimeout.current = setTimeout(() => pollStatus(id), POLL_INTERVAL_MS);
    } catch (err) {
      if (err?.name === "AbortError") return;
      setError(err.message || "Unexpected error while polling");
      setPolling(false);
    }
  }

  useEffect(() => {
    if (!trackingId || !polling) return;

    pollStatus(trackingId);

    return () => {
      if (pollTimeout.current) clearTimeout(pollTimeout.current);
      if (abortRef.current) abortRef.current.abort();
    };
  }, [trackingId, polling]);

  return (
    <div style={{ maxWidth: 480, margin: "2rem auto", padding: "1.5rem", border: "1px solid #ddd", borderRadius: "8px", fontFamily: "sans-serif" }}>
      <h2>Model Training PoC</h2>
      <p>Upload a CSV (≤25 MB) to start training and poll for results.</p>

      <div style={{ marginBottom: "1rem" }}>
        <input type="file" accept=".csv,text/csv" onChange={onFileChange} disabled={polling} />
      </div>

      <button onClick={startTraining} disabled={!file || polling}>Start training</button>

      <div style={{ marginTop: "1rem", minHeight: "1.5rem" }}>{status}</div>

      {trackingId && (
        <div style={{ marginTop: "0.5rem", fontSize: "0.9rem", color: "#555" }}>
          Tracking ID: <code>{trackingId}</code>
        </div>
      )}

      {result && (
        <div style={{ marginTop: "1rem", padding: "0.75rem", background: "#f6ffed", border: "1px solid #b7eb8f", borderRadius: "4px" }}>
          <strong>Result:</strong>
          <pre style={{ whiteSpace: "pre-wrap", marginTop: "0.5rem" }}>
            {typeof result === "string" ? result : JSON.stringify(result, null, 2)}
          </pre>
        </div>
      )}

      {error && (
        <div style={{ marginTop: "1rem", padding: "0.75rem", background: "#fff1f0", border: "1px solid #ffa39e", borderRadius: "4px", color: "#a8071a" }}>
          Error: {error}
        </div>
      )}
    </div>
  );
}
