import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchMachines, type ApiMode } from "./api";
import AddMachineModal from "./components/AddMachineModal";
import MachineDetails from "./components/MachineDetails";
import MachineGrid from "./components/MachineGrid";
import type { Machine } from "./types";

const pollIntervalMs = 5000;

export default function App() {
    const [selectedMachine, setSelectedMachine] = useState<Machine | null>(null);
    const [isAddOpen, setIsAddOpen] = useState(false);
    const [mode, setMode] = useState<ApiMode>("live");

    const { data, isLoading, isError, error, isFetching } = useQuery({
        queryKey: ["machines", mode],
        queryFn: () => fetchMachines(mode),
        refetchInterval: pollIntervalMs,
        refetchIntervalInBackground: true,
        refetchOnWindowFocus: false,
        placeholderData: (previousData) => previousData ?? [],
        retry: false,
    });

    const machines = data ?? [];

    return (
        <div className="min-h-screen bg-[radial-gradient(ellipse_at_top,_#ffffff_0%,_#f2f3f7_55%,_#e5e7eb_100%)] text-slate-900">
            <div className="mx-auto flex max-w-6xl flex-col gap-6 px-4 py-8 sm:px-6 sm:py-10">
                <header className="flex flex-wrap items-center justify-between gap-4 rounded-3xl bg-white px-5 py-5 shadow-[0_24px_50px_rgba(15,23,42,0.12)] sm:gap-6 sm:px-7 sm:py-6">
                    <div className="space-y-2">
                        <p className="text-xs uppercase tracking-[0.3em] text-slate-500">Machine Breakdown Tracker</p>
                        <h1 className="text-xl font-semibold text-slate-900 sm:text-2xl md:text-3xl">
                            Predict TTL for machines
                        </h1>
                    </div>
                    <div className="flex flex-wrap items-center gap-3 text-sm font-semibold text-slate-500">
                        <span className="text-xs sm:text-sm">
                            {isFetching ? "Refreshing data…" : isError ? "API offline" : "Live updates on"}
                        </span>
                        <div className="flex items-center gap-2 rounded-full border border-slate-200 bg-slate-50 px-2 py-1">
                            <button
                                className={`rounded-full px-3 py-1 text-xs font-semibold ${
                                    mode === "live"
                                        ? "bg-slate-900 text-white"
                                        : "text-slate-500 hover:text-slate-700"
                                }`}
                                type="button"
                                onClick={() => setMode("live")}
                            >
                                Live
                            </button>
                            <button
                                className={`rounded-full px-3 py-1 text-xs font-semibold ${
                                    mode === "demo"
                                        ? "bg-slate-900 text-white"
                                        : "text-slate-500 hover:text-slate-700"
                                }`}
                                type="button"
                                onClick={() => setMode("demo")}
                            >
                                Demo
                            </button>
                        </div>
                    </div>
                </header>

                {isError && (
                    <div className="grid gap-2 rounded-2xl border border-rose-200 bg-rose-50 px-5 py-4 text-rose-700">
                        <strong className="text-sm">We could not load machine data.</strong>
                        <span className="text-sm">
                            {error instanceof Error
                                ? error.message
                                : "The service is unavailable right now."}
                        </span>
                    </div>
                )}

                <MachineGrid
                    machines={machines}
                    selectedMachine={selectedMachine}
                    onSelect={setSelectedMachine}
                    onAddMachine={() => setIsAddOpen(true)}
                    isLoading={isLoading}
                />
            </div>

            {selectedMachine && (
                <MachineDetails
                    machine={selectedMachine}
                    onDismiss={() => setSelectedMachine(null)}
                    mode={mode}
                />
            )}

            {isAddOpen && (
                <AddMachineModal
                    onSubmitted={() => setIsAddOpen(false)}
                    onClose={() => setIsAddOpen(false)}
                    mode={mode}
                />
            )}
        </div>
    );
}
