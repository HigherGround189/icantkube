import { useEffect, useState, type FormEvent } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { trainMachine, type ApiMode } from "../api";

type AddMachineModalProps = {
    onSubmitted: () => void;
    onClose: () => void;
    mode: ApiMode;
};

type SubmitState = {
    status: "idle" | "loading" | "success" | "error";
    message?: string;
};

export default function AddMachineModal({ onSubmitted, onClose, mode }: AddMachineModalProps) {
    const queryClient = useQueryClient();
    const [machineName, setMachineName] = useState("");
    const [csvFile, setCsvFile] = useState<File | null>(null);
    const [submitState, setSubmitState] = useState<SubmitState>({ status: "idle" });

    useEffect(() => {
        const handleKeyDown = (event: KeyboardEvent) => {
            if (event.key === "Escape") {
                onClose();
            }
        };

        window.addEventListener("keydown", handleKeyDown);
        return () => window.removeEventListener("keydown", handleKeyDown);
    }, [onClose]);

    const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault();

        if (!machineName.trim()) {
            setSubmitState({ status: "error", message: "Please enter a machine name." });
            return;
        }

        if (!csvFile) {
            setSubmitState({ status: "error", message: "Please attach a CSV file." });
            return;
        }

        try {
            setSubmitState({ status: "loading" });
            await trainMachine(machineName, csvFile, mode);
            setSubmitState({ status: "success", message: "Machine queued for training." });
            setMachineName("");
            setCsvFile(null);
            await queryClient.invalidateQueries({ queryKey: ["machines"] });
            onSubmitted();
        } catch (submitError) {
            setSubmitState({
                status: "error",
                message:
                    submitError instanceof Error
                        ? submitError.message
                        : "Something went wrong while sending the CSV.",
            });
        }
    };

    return (
        <div
            className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 px-4 py-8 backdrop-blur-sm"
            role="dialog"
            aria-modal="true"
            onClick={(event) => {
                if (event.target === event.currentTarget) {
                    onClose();
                }
            }}
        >
            <div className="w-full max-w-lg rounded-3xl bg-white p-5 shadow-[0_30px_70px_rgba(15,23,42,0.25)] sm:p-6">
                <div className="space-y-2">
                    <p className="text-xs uppercase tracking-[0.3em] text-slate-500">New machine</p>
                    <h2 className="text-xl font-semibold text-slate-900">Upload training data</h2>
                    <p className="text-sm text-slate-500">
                        Add a machine name and a CSV file to start model training.
                    </p>
                </div>
                <form className="mt-5 space-y-4 sm:mt-6" onSubmit={handleSubmit}>
                    <label className="block space-y-2 text-sm font-semibold text-slate-700">
                        Machine name
                        <input
                            value={machineName}
                            onChange={(event) => setMachineName(event.target.value)}
                            placeholder="ex: Wittman"
                            type="text"
                            className="w-full rounded-2xl border border-slate-200 px-3 py-3 text-sm focus:border-sky-400 focus:outline-none sm:px-4"
                        />
                    </label>
                    <label className="block space-y-2 text-sm font-semibold text-slate-700">
                        CSV file
                        <input
                            type="file"
                            accept=".csv,text/csv"
                            onChange={(event) => setCsvFile(event.target.files?.[0] ?? null)}
                            className="w-full rounded-2xl border border-slate-200 bg-white px-3 py-3 text-sm file:mr-3 file:rounded-xl file:border-0 file:bg-sky-100 file:px-3 file:py-2 file:text-sm file:font-semibold file:text-sky-700 sm:px-4"
                        />
                    </label>
                    <button
                        className="w-full rounded-2xl bg-sky-500 px-4 py-3 text-sm font-semibold text-white shadow-[0_18px_35px_rgba(14,165,233,0.35)] transition hover:bg-sky-600 disabled:cursor-not-allowed disabled:opacity-60"
                        type="submit"
                        disabled={submitState.status === "loading"}
                    >
                        {submitState.status === "loading" ? "Sending…" : "Send for training"}
                    </button>
                    <button
                        className="w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm font-semibold text-slate-700"
                        type="button"
                        onClick={onClose}
                        disabled={submitState.status === "loading"}
                    >
                        Cancel
                    </button>
                    {submitState.status !== "idle" && submitState.message && (
                        <p
                            className={`rounded-2xl px-4 py-3 text-sm font-medium ${
                                submitState.status === "error"
                                    ? "bg-rose-50 text-rose-600"
                                    : "bg-emerald-50 text-emerald-600"
                            }`}
                        >
                            {submitState.message}
                        </p>
                    )}
                </form>
            </div>
        </div>
    );
}
