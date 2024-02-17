import asyncio

from multiprocessing import Queue as mpQueue, Process
from asyncio import Queue as aioQueue
from threading import Thread
from typing import Callable, NoReturn

from PubSubWs import PubSubWs
from common import WorkerQueues

WorkerFunction = Callable[[WorkerQueues], NoReturn]


class BackgroundTasks:
    def __init__(self):
        self._process_is_dead = False

        self._task_queue: mpQueue = mpQueue()
        self._response_queue: mpQueue = mpQueue()
        self._resp_aio_queue: aioQueue = aioQueue()
        self.worker_queues = WorkerQueues(self._task_queue, self._response_queue)

        self._psw = PubSubWs()

    def setup(self, app, worker_fn):
        self._psw.setup(app, "/ws/attack-progress")

        self._worker_process = Process(target=worker_fn, args=(self.worker_queues,))

        self._response_reading_thread = Thread(target=self._response_reader)

    def start(self):
        self._response_reading_thread.start()
        self._worker_process.start()
        self.receive_data_from_process()

    def shutdown(self):
        self._worker_process.terminate()

        # stop waiting on data to be received from the worker process
        self._process_is_dead = True
        # if we don't flush the queue, the response reader will block indefinitely
        self.worker_queues.flush_response_queue()

        self._worker_process.join()
        self._response_reading_thread.join()

    def _response_reader(self):
        while not self._process_is_dead:
            response = self.worker_queues.get_response()
            self._resp_aio_queue.put_nowait(response)

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
