from enum import Enum
from dataclasses import dataclass

class Status(Enum):
    """ Set up statuses to improve readability and reusability """
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass(frozen=True)
class PipelineConfig:
    experiment_name: str
    pipeline_name: str
    model_name: str
    registered_model_name: str

SAMPLE_CFG = PipelineConfig(
    experiment_name="sample_training_pipeline",
    pipeline_name="iris-pipeline",
    model_name="iris_pipeline_model",
    registered_model_name="IrisPipelineModel",
)