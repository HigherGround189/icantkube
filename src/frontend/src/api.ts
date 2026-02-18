import type { Machine } from "./types";

type MachinesResponse = {
    machines?: unknown;
};

export type ApiMode = "live" | "demo";
export type InferenceServerAction = "start" | "stop";
const apiTimeoutMs = 15000;

type ApiErrorPayload = {
    detail?: string;
    message?: string;
};

const withTimeout = async (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
    const controller = new AbortController();
    const timeout = window.setTimeout(() => controller.abort(), apiTimeoutMs);

    try {
        return await fetch(input, {
            ...init,
            signal: controller.signal,
            credentials: "same-origin",
        });
    } catch (error) {
        if (error instanceof DOMException && error.name === "AbortError") {
            throw new Error("Request timed out. Please try again.");
        }

        throw error;
    } finally {
        window.clearTimeout(timeout);
    }
};

const toApiErrorMessage = async (response: Response, fallback: string): Promise<string> => {
    const body = (await response.json().catch(() => null)) as ApiErrorPayload | null;
    return body?.detail ?? body?.message ?? `${fallback} (${response.status})`;
};

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
        status: "inference",
        lastInferenceResults: [120, 98, 102, 88, 76, 90],
        trainingProgress: null,
    },
    {
        name: "Kestrel-03",
        status: "inference",
        lastInferenceResults: [36, 28, 22, 30, 18, 16],
        trainingProgress: null,
    },
];

type ActiveInferenceServerResponse = unknown[] | { deployments?: unknown };

const extractString = (...candidates: unknown[]): string | null => {
    for (const candidate of candidates) {
        if (typeof candidate === "string" && candidate.trim()) {
            return candidate.trim();
        }
    }
    return null;
};

const toActiveInferenceServerModelName = (item: unknown): string | null => {
    if (!item || typeof item !== "object") {
        return null;
    }

    const record = item as Record<string, unknown>;
    const metadata =
        record.metadata && typeof record.metadata === "object"
            ? (record.metadata as Record<string, unknown>)
            : null;
    const annotations =
        metadata?.annotations && typeof metadata.annotations === "object"
            ? (metadata.annotations as Record<string, unknown>)
            : null;
    const deploymentName = extractString(metadata?.name, record.name);
    const annotationModelName = extractString(
        annotations?.["model-name"],
        annotations?.model_name
    );

    if (annotationModelName) {
        return annotationModelName;
    }

    if (deploymentName && deploymentName.endsWith("-inference-server")) {
        return deploymentName.replace(/-inference-server$/i, "");
    }

    return null;
};

export const fetchMachines = async (mode: ApiMode): Promise<Machine[]> => {
    if (mode === "demo") {
        return demoMachines;
    }

    const response = await withTimeout("/api/machines-data/all");

    if (!response.ok) {
        throw new Error(await toApiErrorMessage(response, "Failed to load machines"));
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

export const fetchActiveInferenceServers = async (mode: ApiMode): Promise<Set<string>> => {
    if (mode === "demo") {
        return new Set<string>();
    }

    const response = await withTimeout("/api/inference-gateway/inference/active-inference-servers");

    if (!response.ok) {
        throw new Error(await toApiErrorMessage(response, "Failed to load active inference servers"));
    }

    const data: ActiveInferenceServerResponse = await response.json();
    const items = Array.isArray(data)
        ? data
        : Array.isArray((data as { deployments?: unknown }).deployments)
            ? ((data as { deployments: unknown[] }).deployments as unknown[])
            : [];

    const modelNames = items
        .map(toActiveInferenceServerModelName)
        .filter((modelName): modelName is string => Boolean(modelName))
        .map((modelName) => modelName.toLowerCase());

    return new Set(modelNames);
};

export const trainMachine = async (name: string, csvFile: File, mode: ApiMode) => {
    if (mode === "demo") {
        return { ok: true };
    }

    const machineName = name.trim();
    if (!machineName) {
        throw new Error("Machine name is required.");
    }

    const csvBody = await csvFile.text();
    const response = await withTimeout(`/api/model-train/start?name=${encodeURIComponent(machineName)}`, {
        method: "POST",
        headers: {
            "Content-Type": "text/csv",
        },
        body: csvBody,
    });

    if (!response.ok) {
        throw new Error(await toApiErrorMessage(response, "Model train request failed"));
    }

    return response;
};

export const setInferenceServer = async (
    modelName: string,
    action: InferenceServerAction,
    mode: ApiMode
) => {
    if (mode === "demo") {
        return { ok: true };
    }

    const normalizedModelName = modelName.trim();
    if (!normalizedModelName) {
        throw new Error("Model name is required.");
    }

    const endpoint =
        action === "start"
            ? "/api/inference-gateway/inference/create-server"
            : "/api/inference-gateway/inference/delete-server";
    const payload =
        action === "start"
            ? { model_name: normalizedModelName, replicas: 1, prediction_interval: 5 }
            : { model_name: normalizedModelName };

    const response = await withTimeout(endpoint, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
    });

    if (!response.ok) {
        throw new Error(await toApiErrorMessage(response, `Failed to ${action} inference server`));
    }

    const responsePayload = (await response.json().catch(() => null)) as
        | { message?: string }
        | null;

    if (
        action === "start" &&
        responsePayload?.message?.toLowerCase().includes("can't create server")
    ) {
        throw new Error(responsePayload.message);
    }

    return { ok: true };
};
