from typing import Optional, Tuple, TypeVar, Generic
from multiprocessing import Queue as mpQueue, Event as mpEvent
from pydantic import BaseModel

class PositionInQueue(BaseModel):
    message_type: str = "PositionInQueue"
    position: int
    total: int

T = TypeVar("T")


# Queue type for attack workers
class WorkerQueue(Generic[T]):
    RequestToken = str
    SentinelTuple = (None, None)

    def __init__(self):
        self._queue = mpQueue()
        self._get_call_event = mpEvent()

    def put(self, request_token: RequestToken, payload: T):
        self._queue.put((request_token, payload))

    def get(self) -> Tuple[RequestToken, T]:
        self._get_call_event.set()
        return self._queue.get()

    def wait_for_get_event(self):
        self._get_call_event.wait()
        self._get_call_event.clear()

    def flush(self):
        self._queue.put(self.SentinelTuple)


# Contains the task and response channels specific to a single worker
class WorkerCommunication:
    def __init__(self):
        self.task_channel = WorkerQueue[AttackParameters]()
        self.response_channel = WorkerQueue[AttackProgress]()


class AttackParameters(BaseModel):
    model: str
    attack: str = "invertinggradients"
    modality: str = "images"
    user_idx: int = 0
    number_of_clients: int = 1
    datasetStructure: str
    csvPath: Optional[str]
    datasetSize: int
    numClasses: int
    batchSize: int
    numRestarts: int
    stepSize: float
    maxIterations: int
    callbackInterval: int
    ptFilePath: Optional[str]
    zipFilePath: Optional[str]
    budget: int


class AttackStatistics(BaseModel):
    MSE: float = 0
    PSNR: float = 0
    SSIM: float = 0


class AttackProgress(BaseModel):
    message_type: str = "AttackProgress"
    current_iteration: int = 0
    max_iterations: int = 0
    current_restart: int = 0
    max_restarts: int = 0
    current_batch: int = 0
    max_batches: int = 0
    time_taken: float = 0
    statistics: AttackStatistics = AttackStatistics()
    true_image: Optional[str] = None # base64 encoded image
    reconstructed_image: Optional[str] = None # base64 encoded image
    error_message: str = None # Optional error message
