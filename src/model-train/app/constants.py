from enum import Enum

class Status(Enum):
    """ Set up statuses to improve readability and reusability """
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"