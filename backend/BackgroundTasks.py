import asyncio

from multiprocessing import Process, Event as mpEvent
from asyncio import (
    Queue as aioQueue,
    run_coroutine_threadsafe,
    Event as aioEvent,
    Lock as aioLock,
)
from threading import Thread
from typing import Callable, NoReturn, Deque, Tuple
from collections import deque

from PubSubWs import PubSubWs
from common import AttackParameters, WorkerCommunication, PositionInQueue

WorkerFunction = Callable[[WorkerCommunication], NoReturn]


# Background task manager, responsible for managing the worker process
# and the communication between the worker process and the web server
class BackgroundTasks:
    def __init__(self):
        self._process_is_dead = False

        self._buffered_request_added = aioEvent()
        self._buffered_requests: Deque[Tuple[str, AttackParameters]] = deque()
        self._buffered_requests_lock = aioLock()
        self._num_buffered_requests_changed = aioEvent()

        self._resp_aio_queue: aioQueue = aioQueue()
        self._worker_queues = WorkerCommunication()

        self._psw = PubSubWs()

    # Setup relevant modules and processes
    def setup(self, app, worker_fn):
        # Creates the websocket server with given base path
        self._psw.setup(app, "/ws/attack-progress")

        self._worker_fn = worker_fn
        self._setup_worker()

        self._response_reading_thread = Thread(
            target=self._response_reader, args=(asyncio.get_event_loop(),)
        )

    def _setup_worker(self):
        self._worker_process = Process(
            target=self._worker_fn, args=(self._worker_queues,)
        )

    # Start the worker proces, the response reader and event loop tasks
    def start(self):
        self._response_reading_thread.start()
        self._worker_process.start()
        self.receive_data_from_process()

    def shutdown(self):
        self._worker_process.terminate()

        # Stop waiting on data to be received from the worker process
        self._process_is_dead = True
        # If we don't flush the queue, the response reader will block indefinitely
        self._worker_queues.response_channel.flush()

        self._worker_process.join()
        self._response_reading_thread.join()

    # Submit a task to the worker process and set async events
    async def submit_task(self, request_token: str, attack_params: AttackParameters):
        async with self._buffered_requests_lock:
            self._buffered_requests.append((request_token, attack_params))
        self._buffered_request_added.set()
        self._num_buffered_requests_changed.set()

    # Broadcast the position in the queue to all clients
    async def _broadcast_position_in_queue(self):
        while True:
            # Trigger is when there is any change to request buffer
            await self._num_buffered_requests_changed.wait()
            self._num_buffered_requests_changed.clear()

            # Publish the position in queue to all clients
            async with self._buffered_requests_lock:
                num_jobs_in_queue = len(self._buffered_requests)
                for i, (req_token, _) in enumerate(self._buffered_requests):
                    await self._psw.publish_serialisable_data(
                        req_token,
                        PositionInQueue(position=i + 1, total=num_jobs_in_queue),
                    )

    # Transfer requests from the buffer to the worker process
    async def _put_requests_to_thread(self):
        while True:
            await asyncio.to_thread(self._worker_queues.task_channel.wait_for_get_event)
            # The worker process is requesting for a new task

            # If there are no buffered requests, then wait until there is one
            if len(self._buffered_requests) == 0:
                await self._buffered_request_added.wait()

            # The Event is set regardless of whether or not the queue is empty, so we need to clear it
            self._buffered_request_added.clear()
            async with self._buffered_requests_lock:
                request_token, payload_data = self._buffered_requests.popleft()
            self._num_buffered_requests_changed.set()

            await asyncio.to_thread(
                self._worker_queues.task_channel.put, request_token, payload_data
            )

    # Transfer worker responses to the main thread response queue
    def _response_reader(self, event_loop):
        while not self._process_is_dead:
            response = self._worker_queues.response_channel.get()

            if response is not None:
                token, progress = response
                if progress is not None and progress.message_type == "error":
                    event_loop.create_task(
                        self._psw.close_tokens_websockets(token, progress.error_message)
                    )

            # Safely push to asyncio queue on the main thread
            run_coroutine_threadsafe(self._resp_aio_queue.put(response), event_loop)

    # Publish responses from main thread to clients
    async def _get_response_from_thread(self):
        while True:
            request_token, response_data = await self._resp_aio_queue.get()

            # Sentinel value received, break the loop
            if request_token is None:
                break

            await self._psw.publish_serialisable_data(request_token, response_data)

    # Add thread tasks to the main event loop
    def receive_data_from_process(self):
        loop = asyncio.get_event_loop()
        loop.create_task(self._get_response_from_thread())
        loop.create_task(self._broadcast_position_in_queue())
        loop.create_task(self._put_requests_to_thread())

    # Cancel a task either in buffer or currently being processed
    async def cancel_task(self, request_token: str):
        in_buffer = False
        async with self._buffered_requests_lock:
            for buffered_request_token, _ in self._buffered_requests:
                if buffered_request_token == request_token:
                    self._buffered_requests.remove((request_token, _))
                    in_buffer = True
                    break

        # Either restart worker to cancel current task or remove from buffer
        if in_buffer:
            self._num_buffered_requests_changed.set()
        else:
            self._restart_worker()

        # Never got result so deregister route
        await self._psw.deregister_route(request_token)

    # Restart the worker process, cancels the current task if exists
    def _restart_worker(self):
        self._worker_process.terminate()
        self._worker_process.join()
        self._setup_worker()
        self._worker_process.start()