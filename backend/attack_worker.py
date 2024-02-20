import base64
from common import WorkerCommunication
from breaching.attack_script import breaching, AttackParameters, AttackProgress, AttackStatistics, setup_attack, perform_attack, get_metrics
import time
import random
import GPUtil
import uuid
# from unittest.mock import Mock

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
        
        #limit_gpu_percentage(data.budget)

        cfg, setup, user, server, attacker, model, loss_fn = setup_attack(attack_params=data, 
                                                                          cfg=None, 
                                                                          torch_model=None)

        response = request_token, queues.response_channel
        r_user_data, t_user_data, server_payload = perform_attack(cfg, setup, user, server, attacker, model, loss_fn, 
                                                                  response=response)
        get_metrics(r_user_data, t_user_data, server_payload, server, cfg, setup, response)

# Limit GPU access with GPUtil
def limit_gpu_percentage(percentage):
    gpus = GPUtil.getGPUs()
    if gpus:
        gpu = gpus[0]  # Assuming you have only one GPU
        gpu.set_power_limit(percentage=percentage)
    else:
        print("No GPU found.")

# Use this for testing?
# if __name__ == "__main__":
#     pars = AttackParameters(
#         model='resnet18',
#         datasetStructure='test',
#         csvPath='nothing',
#         datasetSize=50000,
#         numClasses=10,
#         batchSize=1,
#         numRestarts=1,
#         stepSize=0.1,
#         maxIterations=10,
#         callbackInterval=1,
#         ptFilePath='nothing',
#         zipFilePath='nothing',
#     )

#     req_tok = str(uuid.uuid4())

#     queue = WorkerCommunication()
#     queue.task_channel.put(req_tok, pars)

#     attack_worker(queue)