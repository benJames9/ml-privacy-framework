import base64
from common import WorkerCommunication, AttackProgress, AttackStatistics
from multiprocessing import Event as mpEvent
import time
import random
import GPUtil

def attack_worker(queues: WorkerCommunication, cancel: mpEvent):
    """
    This shows how the worker process should be structured.
    The actual worker should receive the data from the input_queue,
      and run the attack with the given parameters.
    """

    while True:
        print("waiting for data...")
        request_token, data = queues.task_channel.get()
        print(data)
        
        limit_gpu_percentage(data.budget)
        restart = False
        
        time.sleep(1)
        for i in range(10):
            if (cancel.is_set()):
                cancel.clear()
                restart = True
                break
            
            time.sleep(1)
            print(f"doing work {i}")
            queues.response_channel.put(
                request_token, AttackProgress(current_iteration=i, max_iterations=10)
            )
        
        if restart: 
            continue
        
        time.sleep(1)
        stats = AttackStatistics(MSE=random.random(), SSIM=random.random(), PSNR=random.random())

        image_data = None
        with open("./demo.jpg", 'rb') as image_file:
            image_data = image_file.read()
        base64_encoded_data = base64.b64encode(image_data).decode('utf-8')

        queues.response_channel.put(
            request_token, AttackProgress(current_iteration=999, max_iterations=999, statistics=stats, reconstructed_image=base64_encoded_data)
        )

# Limit GPU access with GPUtil
def limit_gpu_percentage(percentage):
    gpus = GPUtil.getGPUs()
    if gpus:
        gpu = gpus[0]  # Assuming you have only one GPU
        gpu.set_power_limit(percentage=percentage)
    else:
        print("No GPU found.")
