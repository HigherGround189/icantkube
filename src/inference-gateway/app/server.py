from pydantic import BaseModel

class Server(BaseModel):
    machine_name: str
    replica_count: int = 1
    