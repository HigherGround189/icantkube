import { useEffect, useMemo, useState } from "react";
import type { Machine } from "../types";
import Chart from "./Chart";
import { toggleInference, type ApiMode } from "../api";

const statusTone = (status: string) => {
    const normalized = status.toLowerCase();

    if (normalized.includes("training")) {
        return "bg-orange-100 text-orange-800";
    }

    if (normalized.includes("on")) {
        return "bg-emerald-100 text-emerald-800";
    }

    if (normalized.includes("off")) {
        return "bg-slate-200 text-slate-700";
    }

    return "bg-slate-200 text-slate-600";
};

type MachineDetailsProps = {
    machine: Machine;
    onDismiss: () => void;
    mode: ApiMode;
};

export default function MachineDetails({ machine, onDismiss, mode }: MachineDetailsProps) {
    const [toggleState, setToggleState] = useState<{
        status: "idle" | "loading" | "success" | "error";
        message?: string;
    }>({ status: "idle" });

    const isTraining = useMemo(
        () => machine.status.toLowerCase().includes("training"),
        [machine.status]
    );
    const isInferenceOn = useMemo(
        () => machine.status.toLowerCase().includes("inference on"),
        [machine.status]
    );

    useEffect(() => {
        const handleKeyDown = (event: KeyboardEvent) => {
            if (event.key === "Escape") {
                onDismiss();
            }
        };

        window.addEventListener("keydown", handleKeyDown);
        return () => window.removeEventListener("keydown", handleKeyDown);
    }, [onDismiss]);

    const handleToggle = async () => {
        try {
            setToggleState({ status: "loading" });
            await toggleInference(machine.name, mode, !isInferenceOn);
            setToggleState({
                status: "success",
                message: isInferenceOn ? "Inference stopped." : "Inference started.",
            });
        } catch (error) {
            setToggleState({
                status: "error",
                message: error instanceof Error ? error.message : "Failed to toggle inference.",
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
                    onDismiss();
                }
            }}
        >
            <section className="w-full max-w-3xl space-y-6 rounded-3xl border border-sky-200/60 bg-white p-5 shadow-[0_30px_70px_rgba(15,23,42,0.25)] sm:p-6">
                <div className="flex flex-wrap items-center justify-between gap-4">
                    <div className="space-y-2">
                        <h2 className="text-lg font-semibold text-slate-900 sm:text-xl">{machine.name}</h2>
                        <span
                            className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold capitalize ${statusTone(
                                machine.status
                            )}`}
                        >
                            {machine.status}
                        </span>
                    </div>
                    <div className="flex items-center gap-3">
                        {!isTraining && (
                            <button
                                className="rounded-full border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700 transition hover:border-sky-300 hover:text-sky-600 disabled:cursor-not-allowed disabled:opacity-60"
                                type="button"
                                onClick={handleToggle}
                                disabled={toggleState.status === "loading"}
                            >
                                {isInferenceOn ? "Stop inference" : "Start inference"}
                            </button>
                        )}
                        <button
                            className="text-sm font-semibold text-sky-600"
                            type="button"
                            onClick={onDismiss}
                        >
                            Close
                        </button>
                    </div>
                </div>

                {isTraining ? (
                    <div className="space-y-3 rounded-2xl border border-dashed border-slate-200 bg-slate-50 px-5 py-6">
                        <p className="text-sm font-semibold text-slate-700">Training in progress</p>
                        <div className="h-2 w-full rounded-full bg-slate-200">
                            <div
                                className="h-2 rounded-full bg-sky-500"
                                style={{ width: `${machine.trainingProgress ?? 0}%` }}
                            />
                        </div>
                        <p className="text-xs text-slate-500">
                            {machine.trainingProgress !== null
                                ? `${machine.trainingProgress}% complete`
                                : "Awaiting progress updates"}
                        </p>
                    </div>
                ) : machine.lastInferenceResults ? (
                    <Chart values={machine.lastInferenceResults} />
                ) : (
                    <div className="rounded-2xl border border-dashed border-slate-200 bg-slate-50 px-5 py-6 text-sm text-slate-500">
                        No breakdown forecasts yet for this machine.
                    </div>
                )}
                {toggleState.status !== "idle" && toggleState.message && (
                    <p
                        className={`text-sm ${
                            toggleState.status === "error" ? "text-rose-600" : "text-emerald-600"
                        }`}
                    >
                        {toggleState.message}
                    </p>
                )}
            </section>
        </div>
    );
}
