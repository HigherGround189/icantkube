import type { Machine } from "../types";
import type { ApiMode, InferenceServerAction } from "../api";

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

type MachineCardProps = {
    machine: Machine;
    isSelected: boolean;
    onSelect: (machine: Machine) => void;
    mode: ApiMode;
    isInferenceServerActive: boolean;
    onToggleInferenceServer: (machineName: string, action: InferenceServerAction) => void;
    isInferenceActionPending: boolean;
};

export default function MachineCard({
    machine,
    isSelected,
    onSelect,
    mode,
    isInferenceServerActive,
    onToggleInferenceServer,
    isInferenceActionPending,
}: MachineCardProps) {
    const action: InferenceServerAction = isInferenceServerActive ? "stop" : "start";
    const actionLabel = isInferenceServerActive ? "Stop server" : "Start server";
    const isDisabled = mode !== "live" || isInferenceActionPending;

    return (
        <div
            className={`flex min-h-[140px] flex-col gap-3 rounded-2xl bg-white px-4 py-4 text-left shadow-[0_22px_45px_rgba(15,23,42,0.12)] transition hover:-translate-y-1 hover:shadow-[0_30px_60px_rgba(15,23,42,0.16)] sm:min-h-[160px] sm:px-5 ${
                isSelected ? "ring-2 ring-sky-300" : ""
            }`}
            onClick={() => onSelect(machine)}
            onKeyDown={(event) => {
                if (event.target !== event.currentTarget) {
                    return;
                }
                if (event.key === "Enter" || event.key === " ") {
                    event.preventDefault();
                    onSelect(machine);
                }
            }}
            role="button"
            tabIndex={0}
        >
            <div className="flex items-center justify-between gap-3">
                <h3 className="text-base font-semibold text-slate-900 sm:text-lg">{machine.name}</h3>
                <span
                    className={`rounded-full px-3 py-1 text-xs font-semibold capitalize ${statusTone(
                        machine.status
                    )}`}
                >
                    {machine.status}
                </span>
            </div>
            <div>
                <p className="text-xs uppercase tracking-[0.16em] text-slate-500">
                    {machine.status.toLowerCase().includes("training")
                        ? "Training progress"
                        : "Hours to breakdown"}
                </p>
                <p className="mt-1 text-sm font-semibold text-slate-900">
                    {machine.status.toLowerCase().includes("training")
                        ? machine.trainingProgress !== null
                            ? `${machine.trainingProgress}%`
                            : "Training queued"
                        : machine.lastInferenceResults
                            ? `${machine.lastInferenceResults[machine.lastInferenceResults.length - 1]} hrs`
                            : "No data yet"}
                </p>
            </div>
            <div className="mt-auto flex items-center justify-between gap-3 pt-1">
                <span className="text-xs text-slate-500">
                    {isInferenceServerActive ? "Inference server active" : "Inference server stopped"}
                </span>
                <button
                    className={`rounded-xl px-3 py-2 text-xs font-semibold transition ${
                        isInferenceServerActive
                            ? "border border-rose-200 bg-rose-50 text-rose-700 hover:bg-rose-100"
                            : "border border-sky-200 bg-sky-50 text-sky-700 hover:bg-sky-100"
                    } disabled:cursor-not-allowed disabled:opacity-60`}
                    type="button"
                    disabled={isDisabled}
                    onClick={(event) => {
                        event.stopPropagation();
                        onToggleInferenceServer(machine.name, action);
                    }}
                >
                    {isInferenceActionPending ? "Working..." : actionLabel}
                </button>
            </div>
        </div>
    );
}
