import type { Machine } from "./types";

type MachinesResponse = {
    machines?: unknown;
};

export type ApiMode = "live" | "demo";

const normalizeResults = (value: unknown): number[] | null => {
    if (Array.isArray(value)) {
        const filtered = value.filter((item) => typeof item === "number");
        return filtered.length > 0 ? filtered : null;
    }

    if (typeof value === "number") {
        return [value];
    }

    return null;
};

const toMachine = (item: Record<string, unknown>): Machine | null => {
    const name =
        (typeof item.name === "string" && item.name.trim()) ||
        (typeof item.machine_name === "string" && item.machine_name.trim()) ||
        (typeof item.machineName === "string" && item.machineName.trim()) ||
        "";

    if (!name) {
        return null;
    }

    const status =
        (typeof item.status === "string" && item.status.trim()) ||
        (typeof item.state === "string" && item.state.trim()) ||
        "unknown";

    const lastInferenceResults = normalizeResults(
        item.last_inference_results ?? item.lastInferenceResults ?? item.lastInference
    );
    const trainingProgressRaw =
        item.training_progress ?? item.trainingProgress ?? item.progress ?? item.training;
    const trainingProgress =
        typeof trainingProgressRaw === "number" && !Number.isNaN(trainingProgressRaw)
            ? Math.min(Math.max(trainingProgressRaw, 0), 100)
            : null;

    return {
        name,
        status,
        lastInferenceResults,
        trainingProgress,
    };
};

const demoMachines: Machine[] = [
    {
        name: "Atlas-01",
        status: "training",
        lastInferenceResults: null,
        trainingProgress: 62,
    },
    {
        name: "Helix-07",
        status: "inference on",
        lastInferenceResults: [120, 98, 102, 88, 76, 90],
        trainingProgress: null,
    },
    {
        name: "Kestrel-03",
        status: "inference off",
        lastInferenceResults: [36, 28, 22, 30, 18, 16],
        trainingProgress: null,
    },
];

export const fetchMachines = async (mode: ApiMode): Promise<Machine[]> => {
    if (mode === "demo") {
        return demoMachines;
    }

    const response = await fetch("/api/machines-data/all");

    if (!response.ok) {
        throw new Error(`Failed to load machines (${response.status})`);
    }

    const data: MachinesResponse | unknown[] = await response.json();
    const items = Array.isArray(data)
        ? data
        : Array.isArray((data as MachinesResponse).machines)
            ? ((data as MachinesResponse).machines as unknown[])
            : null;

    if (!items) {
        throw new Error("Invalid machines response format.");
    }

    return items
        .map((item) => (item && typeof item === "object" ? toMachine(item as Record<string, unknown>) : null))
        .filter((machine): machine is Machine => Boolean(machine));
};

export const getDemoMachines = (): Machine[] => demoMachines;

export const trainMachine = async (name: string, csvFile: File, mode: ApiMode) => {
    if (mode === "demo") {
        return { ok: true };
    }

    const csvBody = await csvFile.text();
    const response = await fetch(`/api/model-train/start?name=${encodeURIComponent(name.trim())}`, {
        method: "POST",
        headers: {
            "Content-Type": "text/csv",
        },
        body: csvBody,
    });

    if (!response.ok) {
        throw new Error(`Model train request failed (${response.status})`);
    }

    return response;
};

export const toggleInference = async (name: string, mode: ApiMode, shouldStart: boolean) => {
    if (mode === "demo") {
        return { ok: true };
    }

    const action = shouldStart ? "start" : "stop";
    const response = await fetch(
        `/api/model-inference/${action}?name=${encodeURIComponent(name.trim())}`,
        { method: "POST" }
    );

    if (!response.ok) {
        throw new Error(`Inference ${action} failed (${response.status})`);
    }

    return response;
};
