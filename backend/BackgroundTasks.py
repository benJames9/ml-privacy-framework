import asyncio

from multiprocessing import Queue as mpQueue, Process
from asyncio import Queue as aioQueue, run_coroutine_threadsafe
from threading import Thread
from typing import Callable, NoReturn, Deque, Tuple
from queue import Queue
from collections import deque

from PubSubWs import PubSubWs
from common import AttackParameters, WorkerCommunication

WorkerFunction = Callable[[WorkerCommunication], NoReturn]


# class AsyncThreadProcessCommunication:
#     def __init__(self, channel: WorkerChannel):
#         self._send_queue = Queue()
#         self._aio_recv_queue = aioQueue()

#         event_loop = asyncio.get_event_loop()
#         self._recv_thread = Thread(target=self._recv_from_process, args=(event_loop,))
#         self._send_thread = Thread(target=self._send_to_process)

#         self._stop_communication = False
#         self._channel = channel

#     def _recv_from_process(self, event_loop):
#         while not self._stop_communication:
#             data = self._channel.get()
#             run_coroutine_threadsafe(self._aio_recv_queue.put(data), event_loop)

#     def _send_to_process(self):
#         while not self._stop_communication:
#             request_token, payload_data = self._send_queue.get()
#             self._channel.put(request_token, payload_data)

#     def send(self, request_token, payload_data):
#         self._send_queue.put((request_token, payload_data))


class BackgroundTasks:
    def __init__(self):
        self._process_is_dead = False
        
        self._req_aio_queue: aioQueue = aioQueue()
        self._buffered_requests: Deque[Tuple[str, AttackParameters]] = deque()
        self._should_buffer_requests = True # always buffer, until the worker process requests for a task

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
            print(self._req_aio_queue.qsize(), " IS THE NUMBER OF ITEMS IN THE QUEUE ----------------------------------------------->>>>>>>>>>>>>>>>>>>>>>>>>")
            self._req_aio_queue.put_nowait((request_token, attack_params))
            self._should_buffer_requests = True # set the flag to buffer requests again
        else:
            print(" -------------- BUFFERING A REQUEST -------------- ")
            self._buffered_requests.append((request_token, attack_params))
            
    async def _broadcast_position_in_queue(self):
        while True:
            await asyncio.sleep(1)
            print("Broadcasting position in queue, current buffered queue length is ", len(self._buffered_requests))
            for i, (req_token, _) in enumerate(self._buffered_requests):
                await self._psw.publish(req_token, str(i + 1))

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
            
            print("Sending request to worker process")
            print(f"req q size: {self._req_aio_queue.qsize()}, buffered q size: {len(self._buffered_requests)}, task queue empty: {self._worker_queues.task_channel._queue.empty()}")
            await asyncio.to_thread(self._worker_queues.task_channel.put, request_token, payload_data)

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

            await self._psw.publish(request_token, response_data)

    def receive_data_from_process(self):
        loop = asyncio.get_event_loop()
        loop.create_task(self._get_response_from_thread())
        loop.create_task(self._broadcast_position_in_queue())
        loop.create_task(self._put_responses_to_thread())
