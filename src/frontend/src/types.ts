export type MachineStatus = "training" | "inference_off" | "inference_on" | string;

export type Machine = {
    name: string;
    status: MachineStatus;
    lastInferenceResults: number[] | null;
    trainingProgress: number | null;
};
