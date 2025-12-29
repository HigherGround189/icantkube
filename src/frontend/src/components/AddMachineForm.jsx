import styles from "../App.module.css";

export default function AddMachineForm({ addForm, setAddForm, onSubmit }) {
  return (
    <form className={styles.addForm} onSubmit={onSubmit}>
      <input
        className={styles.input}
        placeholder="Machine name"
        value={addForm.name}
        onChange={(e) => setAddForm((f) => ({ ...f, name: e.target.value }))}
        required
      />
      <input
        className={styles.input}
        placeholder="Image URL (optional)"
        value={addForm.imageUrl}
        onChange={(e) => setAddForm((f) => ({ ...f, imageUrl: e.target.value }))}
      />
      <button className={styles.primaryButton} type="submit">
        Add machine
      </button>
    </form>
  );
}
