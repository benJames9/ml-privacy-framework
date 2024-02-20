from typing import Optional, Tuple, TypeVar, Generic
from multiprocessing import Queue as mpQueue, Event as mpEvent
from pydantic import BaseModel

class PositionInQueue(BaseModel):
    message_type = "PositionInQueue"
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
