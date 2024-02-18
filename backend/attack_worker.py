import base64
from common import WorkerCommunication, AttackProgress, AttackStatistics
import time
import random


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
            queues.response_channel.put(
                request_token, AttackProgress(current_iteration=i, max_iterations=10)
            )

        time.sleep(1)
        stats = AttackStatistics(MSE=random.random(), SSIM=random.random(), PSNR=random.random())

        image_data = None
        with open("./demo.jpg", 'rb') as image_file:
            image_data = image_file.read()
        base64_encoded_data = base64.b64encode(image_data).decode('utf-8')

        queues.response_channel.put(
            request_token, AttackProgress(current_iteration=999, max_iterations=999, statistics=stats, reconstructed_image=base64_encoded_data)
        )
