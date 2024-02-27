import base64
from BreachingAdapter import BreachingAdapter
from common import WorkerCommunication
from multiprocessing import Event as mpEvent
import time
import random
import GPUtil
import uuid
import os
# from unittest.mock import Mock

def attack_worker(queues: WorkerCommunication):
    """
    This shows how the worker process should be structured.
    The actual worker should receive the data from the input_queue,
      and run the attack with the given parameters.
    """
    breaching = BreachingAdapter(queues.response_channel)
    while True:
        print("waiting for data...")
        request_token, data = queues.task_channel.get()
        print(data)
        
        # limit_gpu_percentage(data.budget)

        cfg, setup, user, server, attacker, model, loss_fn = breaching.setup_attack(attack_params=data, 
                                                                          cfg=None, 
                                                                          torch_model=None)

        response = request_token, queues.response_channel
        r_user_data, t_user_data, server_payload = breaching.perform_attack(cfg, setup, user, server, attacker, model, loss_fn, request_token=request_token)
        breaching.get_metrics(r_user_data, t_user_data, server_payload, server, cfg, setup, response)

# Limit GPU access with GPUtil
def limit_gpu_percentage(percentage):
    gpus = GPUtil.getGPUs()
    if gpus:
        gpu = gpus[0]  # Assuming you have only one GPU
        gpu.set_power_limit(percentage=percentage)
    else:
        print("No GPU found.")

# Use this for testing?
if __name__ == "__main__":
    pars = AttackParameters(
        model='ResNet-18',
        datasetStructure='folders',
        csvPath='~/data',
        datasetSize=350,
        numClasses=7,
        batchSize=1,
        numRestarts=1,
        stepSize=0.1,
        maxIterations=1,
        callbackInterval=10,
        ptFilePath='resnet18_pretrained.pt',
        zipFilePath='small_foldered_set.zip',
        budget=100
    )

    req_tok = str(uuid.uuid4())

    queue = WorkerCommunication()
    queue.task_channel.put(req_tok, pars)

    attack_worker(queue)