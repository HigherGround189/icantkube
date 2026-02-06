import { useEffect, useMemo } from "react";
import type { Machine } from "../types";
import Chart from "./Chart";

const statusTone = (status: string) => {
    const normalized = status.toLowerCase();

    if (normalized.includes("training")) {
        return "bg-orange-100 text-orange-800";
    }

    if (normalized.includes("inference")) {
        return "bg-emerald-100 text-emerald-800";
    }

    return "bg-slate-200 text-slate-600";
};

type MachineDetailsProps = {
    machine: Machine;
    onDismiss: () => void;
};

export default function MachineDetails({ machine, onDismiss }: MachineDetailsProps) {
    const isTraining = useMemo(
        () => machine.status.toLowerCase().includes("training"),
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
                    <button
                        className="text-sm font-semibold text-sky-600"
                        type="button"
                        onClick={onDismiss}
                    >
                        Close
                    </button>
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
            </section>
        </div>
    );
}
