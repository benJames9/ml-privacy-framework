from common import WorkerCommunication
import time

def attack_worker(queues: WorkerCommunication):
    """
    This shows how the worker process should be structured.
    The actual worker should receive the data from the input_queue,
      and run the attack with the given parameters.
    """

    while True:
        print("waiting for data...")
        request_token, data = queues.task_channel.get()
        print(data)
        
        time.sleep(1)
        for i in range(10):
            time.sleep(1)
            print(f"doing work {i}")
            queues.response_channel.put(request_token, f"working on subtask {i}")
        
        time.sleep(1)
        queues.response_channel.put(request_token, "done - we have finished the task")
