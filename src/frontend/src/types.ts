export type MachineStatus = "training" | "inference" | string;

export type Machine = {
    name: string;
    status: MachineStatus;
    lastInferenceResults: number[] | null;
    trainingProgress: number | null;
};
