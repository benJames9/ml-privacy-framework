from common import WorkerQueues
import time

def attack_worker(queues: WorkerQueues):
    """
    This shows how the worker process should be structured.
    The actual worker should receive the data from the input_queue,
      and run the attack with the given parameters.
    """

    while True:
        print("waiting for data...")
        request_token, data = queues.get_task()
        print(data)
        time.sleep(1)
        queues.put_response(request_token, "done - we got the data")
