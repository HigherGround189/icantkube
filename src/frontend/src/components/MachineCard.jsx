import styles from "../App.module.css";

const placeholderSvg =
  "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='200' height='120' viewBox='0 0 200 120' fill='none'><rect width='200' height='120' rx='12' fill='%23f3f4f6'/><path d='M50 75l20-24 16 20 18-28 26 32H50z' stroke='%239ca3af' stroke-width='4' stroke-linejoin='round' fill='none'/><circle cx='74' cy='44' r='7' fill='%239ca3af'/></svg>";

export default function MachineCard({
  machine,
  state,
  onFileChange,
  onStartUpload,
  onDelete,
  onInferenceChange,
  onRunInference,
}) {
  const uploadProgress = state.progress ?? 0;
  const showInference = state.trainingStatus === "completed" && state.modelId;

  return (
    <div className={styles.card}>
      <div className={styles.cardHeader}>
        <div className={styles.machineInfo}>
          <img
            src={machine.imageUrl || placeholderSvg}
            alt={machine.name}
            className={styles.machineImage}
          />
          <div>
            <div className={styles.machineName}>{machine.name}</div>
            <div className={styles.machineMeta}>ID: {machine.id}</div>
          </div>
        </div>
        <button
          className={styles.dangerButton}
          onClick={() => onDelete(machine.id)}
          disabled={state.deleting}
        >
          {state.deleting ? "Deleting..." : "Delete"}
        </button>
      </div>

      <div className={styles.section}>
        <div className={styles.sectionTitle}>Training data</div>
        <input
          type="file"
          accept=".csv,text/csv"
          onChange={(e) => onFileChange(machine.id, e.target.files?.[0] || null)}
          disabled={state.uploading}
        />
        {state.fileError && <div className={styles.errorText}>{state.fileError}</div>}
        <button
          className={styles.primaryButton}
          onClick={() => onStartUpload(machine.id)}
          disabled={!state.file || state.uploading}
        >
          {state.uploading ? "Uploading..." : "Upload & Train"}
        </button>
        <div className={styles.statusRow}>
          <div>{state.statusMessage}</div>
          {state.trackingId && <code className={styles.code}>tracking: {state.trackingId}</code>}
        </div>
        <div className={styles.progressBarOuter}>
          <div className={styles.progressBarInner} style={{ width: `${uploadProgress}%` }} />
        </div>
        {state.result && (
          <div className={styles.resultBox}>
            <strong>Training result:</strong>
            <pre className={styles.pre}>{JSON.stringify(state.result, null, 2)}</pre>
          </div>
        )}
        {state.error && <div className={styles.errorBox}>Error: {state.error}</div>}
      </div>

      {showInference && (
        <div className={styles.section}>
          <div className={styles.sectionTitle}>Inference</div>
          <textarea
            className={styles.textarea}
            rows={3}
            placeholder="Enter input payload..."
            value={state.inferenceInput}
            onChange={(e) => onInferenceChange(machine.id, e.target.value)}
          />
          <button
            className={styles.primaryButton}
            onClick={() => onRunInference(machine.id)}
            disabled={state.runningInference}
          >
            {state.runningInference ? "Running..." : "Run inference"}
          </button>
          {state.inferenceResult && (
            <div className={styles.resultBox}>
              <strong>Inference result:</strong>
              <pre className={styles.pre}>{JSON.stringify(state.inferenceResult, null, 2)}</pre>
            </div>
          )}
          {state.inferenceError && <div className={styles.errorBox}>Error: {state.inferenceError}</div>}
        </div>
      )}
    </div>
  );
}
