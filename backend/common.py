from typing import Optional, Tuple, TypeVar, Generic
from multiprocessing import Queue as mpQueue, Event as mpEvent
from pydantic import BaseModel


class AttackParameters(BaseModel):
    model: str
    datasetStructure: str
    csvPath: Optional[str]
    datasetSize: int
    numClasses: int
    batchSize: int
    numRestarts: int
    stepSize: int
    maxIterations: int
    callbackInterval: int
    ptFilePath: Optional[str]
    zipFilePath: Optional[str]


class PositionInQueue(BaseModel):
    position: int
    total: int


class AttackStatistics(BaseModel):
    MSE: float = 0
    PSNR: float = 0
    SSIM: float = 0


class AttackProgress(BaseModel):
    current_iteration: int = 0
    max_iterations: int = 0
    current_restart: int = 0
    max_restarts: int = 0
    current_batch: int = 0
    max_batches: int = 0
    time_taken: float = 0
    statistics: AttackStatistics = AttackStatistics()


T = TypeVar("T")


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


class WorkerCommunication:
    def __init__(self):
        self.task_channel = WorkerQueue[AttackParameters]()
        self.response_channel = WorkerQueue[AttackProgress]()
