import { useMemo } from "react";
import type { Machine } from "../types";
import MachineCard from "./MachineCard";

type MachineGridProps = {
    machines: Machine[];
    selectedMachine: Machine | null;
    onSelect: (machine: Machine) => void;
    onAddMachine: () => void;
    isLoading: boolean;
};

type GridItem = { type: "machine"; machine: Machine } | { type: "add" };

export default function MachineGrid({
    machines,
    selectedMachine,
    onSelect,
    onAddMachine,
    isLoading,
}: MachineGridProps) {
    const gridItems = useMemo<GridItem[]>(() => {
        const firstRow = machines.slice(0, 3);
        const remaining = machines.slice(3);
        return [
            ...firstRow.map((machine) => ({ type: "machine" as const, machine })),
            { type: "add" as const },
            ...remaining.map((machine) => ({ type: "machine" as const, machine })),
        ];
    }, [machines]);

    return (
        <section className="relative grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            {gridItems.map((item, index) => {
                if (item.type === "machine") {
                    return (
                        <MachineCard
                            key={`${item.machine.name}-${index}`}
                            machine={item.machine}
                            isSelected={selectedMachine?.name === item.machine.name}
                            onSelect={onSelect}
                        />
                    );
                }

                return (
                    <button
                        key="add-machine"
                        className="flex min-h-[140px] flex-col gap-3 rounded-2xl border border-dashed border-sky-300 bg-sky-50/60 px-4 py-4 text-left shadow-[0_16px_35px_rgba(15,23,42,0.08)] sm:min-h-[160px] sm:px-5"
                        onClick={onAddMachine}
                        type="button"
                    >
                        <div className="grid h-11 w-11 place-items-center rounded-2xl bg-sky-100 text-2xl font-semibold text-sky-600">
                            +
                        </div>
                        <p className="text-base font-semibold text-slate-900">Add machine</p>
                        <p className="text-sm text-slate-500">Upload CSV to train a new model.</p>
                    </button>
                );
            })}

            {isLoading && machines.length === 0 && (
                <div className="absolute -bottom-7 right-2 text-xs text-slate-500">
                    Loading machine data…
                </div>
            )}
        </section>
    );
}
