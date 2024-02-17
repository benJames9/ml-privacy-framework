from dataclasses import dataclass
from typing import Optional, Tuple
from multiprocessing import Queue as mpQueue


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


class WorkerQueues:
    RequestToken = str
    SentinelTuple = (None, None)

    def __init__(self, task_queue: mpQueue, response_queue: mpQueue):
        self.task_queue = task_queue
        self.response_queue = response_queue

    def put_response(self, request_token: RequestToken, response: str):
        self.response_queue.put((request_token, response))

    def put_task(self, request_token: RequestToken, attack_params: AttackParameters):
        self.task_queue.put((request_token, attack_params))

    def get_response(self) -> Tuple[RequestToken, AttackParameters]:
        return self.response_queue.get()

    def get_task(self) -> Tuple[RequestToken, AttackParameters]:
        return self.task_queue.get()

    def flush_response_queue(self):
        self.response_queue.put(self.SentinelTuple)
