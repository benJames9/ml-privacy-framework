import asyncio

from multiprocessing import Process
from asyncio import Queue as aioQueue, run_coroutine_threadsafe
from threading import Thread
from typing import Callable, NoReturn, Deque, Tuple
from collections import deque

from PubSubWs import PubSubWs
from common import AttackParameters, WorkerCommunication, PositionInQueue

WorkerFunction = Callable[[WorkerCommunication], NoReturn]


class BackgroundTasks:
    def __init__(self):
        self._process_is_dead = False

        self._req_aio_queue: aioQueue = aioQueue()
        self._buffered_requests: Deque[Tuple[str, AttackParameters]] = deque()
        self._should_buffer_requests = (
            True  # always buffer, until the worker process requests for a task
        )

        self._resp_aio_queue: aioQueue = aioQueue()
        self._worker_queues = WorkerCommunication()

        self._psw = PubSubWs()

    def setup(self, app, worker_fn):
        self._psw.setup(app, "/ws/attack-progress")

        self._worker_process = Process(target=worker_fn, args=(self._worker_queues,))

        self._response_reading_thread = Thread(
            target=self._response_reader, args=(asyncio.get_event_loop(),)
        )

    def start(self):
        self._response_reading_thread.start()
        self._worker_process.start()
        self.receive_data_from_process()

    def shutdown(self):
        self._worker_process.terminate()

        # stop waiting on data to be received from the worker process
        self._process_is_dead = True
        # if we don't flush the queue, the response reader will block indefinitely
        self._worker_queues.response_channel.flush()

        self._worker_process.join()
        self._response_reading_thread.join()

    def submit_task(self, request_token: str, attack_params: AttackParameters):
        if not self._should_buffer_requests:
            self._req_aio_queue.put_nowait((request_token, attack_params))
            self._should_buffer_requests = True  # set the flag to buffer requests again
        else:
            self._buffered_requests.append((request_token, attack_params))

    async def _broadcast_position_in_queue(self):
        while True:
            await asyncio.sleep(1)
            num_jobs_in_queue = len(self._buffered_requests)
            for i, (req_token, _) in enumerate(self._buffered_requests):
                await self._psw.publish_serialisable_data(
                    req_token, PositionInQueue(position=i + 1, total=num_jobs_in_queue)
                )

    async def _put_responses_to_thread(self):
        while True:
            await asyncio.to_thread(self._worker_queues.task_channel.wait_for_get_event)
            # the worker process is requesting for a new task

            # so check the buffer for any tasks
            request_token, payload_data = None, None
            if len(self._buffered_requests) != 0:
                request_token, payload_data = self._buffered_requests.popleft()
            else:
                # if there are no tasks in the buffer, then we set a flag and wait for a new task to be submitted
                self._should_buffer_requests = False
                request_token, payload_data = await self._req_aio_queue.get()

            await asyncio.to_thread(
                self._worker_queues.task_channel.put, request_token, payload_data
            )

    def _response_reader(self, event_loop):
        while not self._process_is_dead:
            response = self._worker_queues.response_channel.get()

            # safely push to asyncio queue on the main thread
            run_coroutine_threadsafe(self._resp_aio_queue.put(response), event_loop)

    async def _get_response_from_thread(self):
        while True:
            request_token, response_data = await self._resp_aio_queue.get()

            # Sentinel value received, break the loop
            if request_token is None:
                break

            await self._psw.publish_serialisable_data(request_token, response_data)

    def receive_data_from_process(self):
        loop = asyncio.get_event_loop()
        loop.create_task(self._get_response_from_thread())
        loop.create_task(self._broadcast_position_in_queue())
        loop.create_task(self._put_responses_to_thread())
