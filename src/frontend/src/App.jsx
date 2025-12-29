import { useEffect, useMemo, useRef, useState } from "react";
import AddMachineForm from "./components/AddMachineForm";
import MachineCard from "./components/MachineCard";
import styles from "./App.module.css";

const CHUNK_SIZE = 1 * 1024 * 1024; // 1 MB
const MAX_FILE_SIZE = 25 * 1024 * 1024; // 25 MB cap for this UI
const POLL_INTERVAL_MS = 2000;

const initialMachineState = () => ({
  file: null,
  fileError: "",
  uploading: false,
  progress: 0,
  uploadId: "",
  trackingId: "",
  trainingStatus: "",
  statusMessage: "",
  result: null,
  error: "",
  inferenceInput: "",
  inferenceResult: null,
  inferenceError: "",
  runningInference: false,
  modelId: null,
  deleting: false,
});

export default function App() {
  const [machines, setMachines] = useState([]);
  const [loading, setLoading] = useState(true);
  const [addForm, setAddForm] = useState({ name: "", imageUrl: "" });
  const pollTimers = useRef({});
  const [machineStates, setMachineStates] = useState({});

  const mergedMachines = useMemo(
    () =>
      machines.map((machine) => ({
        ...machine,
        state: machineStates[machine.id] || initialMachineState(),
      })),
    [machines, machineStates]
  );

  useEffect(() => {
    loadMachines();
    return () => {
      Object.values(pollTimers.current).forEach((timer) => clearTimeout(timer));
    };
  }, []);

  function updateMachineState(id, updater) {
    setMachineStates((prev) => ({
      ...prev,
      [id]: { ...(prev[id] || initialMachineState()), ...updater },
    }));
  }

  async function loadMachines() {
    setLoading(true);
    try {
      const res = await fetch("/api/models");
      const data = await res.json();
      const list = data.machines || data || [];
      setMachines(list);
      const initialState = {};
      list.forEach((m) => {
        initialState[m.id] = initialMachineState();
        if (m.latestModelId) {
          initialState[m.id].modelId = m.latestModelId;
          initialState[m.id].trainingStatus = m.latestModelStatus || "completed";
        }
      });
      setMachineStates(initialState);
    } catch (err) {
      console.error("Failed to load machines", err);
    } finally {
      setLoading(false);
    }
  }

  function handleFileChange(machineId, file) {
    if (!file) {
      updateMachineState(machineId, { file: null, fileError: "" });
      return;
    }
    if (file.size > MAX_FILE_SIZE) {
      updateMachineState(machineId, { file: null, fileError: "File exceeds 25 MB limit." });
      return;
    }
    updateMachineState(machineId, {
      file,
      fileError: "",
      progress: 0,
      error: "",
      result: null,
      statusMessage: "",
      inferenceResult: null,
      inferenceError: "",
    });
  }

  async function startUpload(machineId) {
    const state = machineStates[machineId] || initialMachineState();
    if (!state.file) {
      updateMachineState(machineId, { fileError: "Select a CSV file first." });
      return;
    }

    updateMachineState(machineId, { uploading: true, progress: 0, statusMessage: "Uploading...", error: "" });

    let uploadId = state.uploadId || "";
    const file = state.file;
    const totalChunks = Math.ceil(file.size / CHUNK_SIZE);

    for (let index = 0; index < totalChunks; index++) {
      const start = index * CHUNK_SIZE;
      const end = Math.min(start + CHUNK_SIZE, file.size);
      const blob = file.slice(start, end);
      const isLast = index === totalChunks - 1;

      const form = new FormData();
      form.append("machineId", machineId);
      form.append("filename", file.name);
      form.append("chunkIndex", String(index));
      form.append("isLast", String(isLast));
      form.append("chunk", new File([blob], file.name, { type: file.type || "text/csv" }));
      if (uploadId) {
        form.append("uploadId", uploadId);
      }

      try {
        const res = await fetch("/api/model-train/chunk", {
          method: "POST",
          body: form,
        });
        if (!res.ok) {
          const message = await res.text();
          throw new Error(message || "Upload failed");
        }
        const data = await res.json();
        uploadId = data.uploadId || uploadId;
        if (isLast && data.trackingId) {
          updateMachineState(machineId, {
            trackingId: data.trackingId,
            trainingStatus: "running",
            statusMessage: "Training started...",
            modelId: data.modelId || null,
          });
          pollTraining(machineId, data.trackingId);
        }
      } catch (err) {
        updateMachineState(machineId, {
          uploading: false,
          error: err.message || "Upload error",
          statusMessage: "",
        });
        return;
      }

      const progressPercent = Math.round(((index + 1) / totalChunks) * 100);
      updateMachineState(machineId, { progress: progressPercent });
    }

    updateMachineState(machineId, {
      uploading: false,
      uploadId,
      statusMessage: "Upload complete. Waiting for training...",
    });
  }

  function pollTraining(machineId, trackingId) {
    clearTimeout(pollTimers.current[machineId]);
    pollTimers.current[machineId] = setTimeout(async () => {
      try {
        const res = await fetch(`/api/model-train/status/${trackingId}`);
        if (!res.ok) {
          throw new Error("Failed to fetch training status");
        }
        const data = await res.json();
        const status = data.status || "unknown";
        const statusMessage = data.progress ? `Status: ${status} (${data.progress}%)` : `Status: ${status}`;

        if (status === "completed") {
          updateMachineState(machineId, {
            trainingStatus: "completed",
            statusMessage: statusMessage || "Training completed",
            result: data.result || {},
            modelId: data.modelId || data.trainedModelId || null,
            progress: 100,
          });
          clearTimeout(pollTimers.current[machineId]);
          return;
        }
        if (status === "failed") {
          updateMachineState(machineId, {
            trainingStatus: "failed",
            statusMessage: "Training failed",
            error: data.error || "Training failed",
          });
          clearTimeout(pollTimers.current[machineId]);
          return;
        }

        updateMachineState(machineId, { trainingStatus: status, statusMessage });
        pollTraining(machineId, trackingId);
      } catch (err) {
        updateMachineState(machineId, {
          statusMessage: "Error polling status",
          error: err.message || "Polling error",
        });
      }
    }, POLL_INTERVAL_MS);
  }

  async function handleAddMachine(e) {
    e.preventDefault();
    if (!addForm.name.trim()) return;
    try {
      const res = await fetch("/api/models", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: addForm.name.trim(), imageUrl: addForm.imageUrl.trim() || undefined }),
      });
      if (!res.ok) {
        throw new Error(await res.text());
      }
      const data = await res.json();
      const newMachine = data.machine || data;
      setMachines((prev) => [...prev, newMachine]);
      setMachineStates((prev) => ({ ...prev, [newMachine.id]: initialMachineState() }));
      setAddForm({ name: "", imageUrl: "" });
    } catch (err) {
      alert(err.message || "Failed to add machine");
    }
  }

  async function handleDeleteMachine(id) {
    updateMachineState(id, { deleting: true });
    try {
      const res = await fetch(`/api/models/${id}`, { method: "DELETE" });
      if (!res.ok) {
        throw new Error(await res.text());
      }
      setMachines((prev) => prev.filter((m) => m.id !== id));
    } catch (err) {
      alert(err.message || "Failed to delete machine");
    } finally {
      updateMachineState(id, { deleting: false });
    }
  }

  function handleInferenceChange(machineId, value) {
    updateMachineState(machineId, { inferenceInput: value, inferenceError: "", inferenceResult: null });
  }

  async function handleRunInference(machineId) {
    const state = machineStates[machineId] || initialMachineState();
    if (!state.modelId) {
      updateMachineState(machineId, { inferenceError: "No trained model available." });
      return;
    }
    updateMachineState(machineId, { runningInference: true, inferenceError: "", inferenceResult: null });
    try {
      const res = await fetch("/api/model-inference", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          modelId: state.modelId,
          machineId,
          payload: state.inferenceInput || "",
        }),
      });
      if (!res.ok) {
        throw new Error(await res.text());
      }
      const data = await res.json();
      updateMachineState(machineId, { inferenceResult: data, runningInference: false });
    } catch (err) {
      updateMachineState(machineId, { inferenceError: err.message || "Inference failed", runningInference: false });
    }
  }

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <div>
          <div className={styles.badge}>AI Lab</div>
          <h1 className={styles.title}>Machine Model Trainer</h1>
          <p className={styles.subtitle}>Manage machines, upload CSVs in 1 MB chunks, train models, and run inference.</p>
        </div>
      </header>

      <section className={styles.addSection}>
        <h2 className={styles.sectionTitle}>Add a machine</h2>
        <AddMachineForm addForm={addForm} setAddForm={setAddForm} onSubmit={handleAddMachine} />
      </section>

      {loading ? (
        <div className={styles.loading}>Loading machines...</div>
      ) : machines.length === 0 ? (
        <div className={styles.emptyState}>
          <p>No machines yet. Add one to get started.</p>
        </div>
      ) : (
        <div className={styles.grid}>
          {mergedMachines.map((machine) => (
            <MachineCard
              key={machine.id}
              machine={machine}
              state={machine.state}
              onFileChange={handleFileChange}
              onStartUpload={startUpload}
              onDelete={handleDeleteMachine}
              onInferenceChange={handleInferenceChange}
              onRunInference={handleRunInference}
            />
          ))}
        </div>
      )}
    </div>
  );
}
