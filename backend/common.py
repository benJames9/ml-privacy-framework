from typing import Optional, Tuple, TypeVar, Generic, List
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


class MiaParams(BaseModel):
    N: int
    data_points: int
    epochs: int
    batch_size: int
    lr: float
    target_label: str
    target_image_path: str
    path_to_label_csv: str


class MiaStatistics(BaseModel):
    likelihood_ratio: float


class BreachingParams(BaseModel):
    modality: str = "images"
    # Image params
    datasetStructure: Optional[str] = "Foldered"
    csvPath: Optional[str] = None
    means: Optional[List[float]] = [0.46, 0.56, 0.57]
    stds: Optional[List[float]] = [0.32, 0.28, 0.27]
    # Text params
    textDataset: Optional[str] = None
    textDataPoints: Optional[int] = None
    seqLength: Optional[int] = None
    tokenizer: Optional[str] = None
    # Attack params
    batchSize: Optional[int]
    numRestarts: int
    stepSize: float
    maxIterations: int
    budget: int = 100
    reconstruction_frequency: int = 10
    tokenizer: Optional[str] = "gpt2"
    shape: Optional[List[int]] = [16]


class AttackParameters(BaseModel):
    model: str
    attack: str = "invertinggradients"
    ptFilePath: Optional[str]
    zipFilePath: Optional[str]
    breaching_params: Optional[BreachingParams] = None
    mia_params: Optional[MiaParams] = None


class AttackStatistics(BaseModel):
    MSE: float = 0
    PSNR: float = 0
    SSIM: float = 0
    FMSE: float = 0
    GBLEU: float = 0
    ACC: float = 0


class AttackProgress(BaseModel):
    message_type: str = "AttackProgress"
    attack_type: str = ""
    attack_start_time_s: int = 0
    current_iteration: int = 0
    max_iterations: int = 0
    current_restart: int = 0
    max_restarts: int = 0
    current_batch: int = 0
    max_batches: int = 0
    time_taken: float = 0
    statistics: AttackStatistics = AttackStatistics()
    error_message: str = None  # Optional error message

    # inverting gradients
    true_image: Optional[str] = None  # base64 encoded image
    reconstructed_image: Optional[str] = None  # base64 encoded image
    reconstructed_images_archive: Optional[str]  # base64 encoded zip file

    # tag attacks
    true_text: Optional[str] = None
    reconstructed_text: Optional[str] = None

    # mia attacks
    mia_stats: Optional[MiaStatistics] = None
