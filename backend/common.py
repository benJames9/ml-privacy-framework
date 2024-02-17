from dataclasses import dataclass
from typing import Optional, Tuple, TypeVar, Generic
from multiprocessing import Queue as mpQueue, Event as mpEvent


@dataclass
class AttackParameters:
    model: str
    datasetStructure: str
    csvPath: str
    datasetSize: int
    numClasses: int
    batchSize: int
    numRestarts: int
    stepSize: int
    maxIterations: int
    callbackInterval: int
    ptFilePath: Optional[str] = None
    zipFilePath: Optional[str] = None


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
        self.response_channel = WorkerQueue[str]()
