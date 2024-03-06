import base64
from MiaAdapter import MiaAdapter
from BreachingAdapter import BreachingAdapter
from common import WorkerCommunication, AttackProgress
from multiprocessing import Event as mpEvent
import time
import random
import GPUtil
import uuid
import os
# from unittest.mock import Mock


# Attack worker function to run on separate process and complete attacks
def attack_worker(queues: WorkerCommunication):
    """
    This shows how the worker process should be structured.
    The actual worker should receive the data from the input_queue,
      and run the attack with the given parameters.
    """
    
    # Initialise adapters for different attacks
    breaching = BreachingAdapter(queues.response_channel)
    mia = MiaAdapter()
    
    # Permenantly loop, fetching data from queues
    while True:
        print("waiting for data...")
        request_token, data = queues.task_channel.get()
        print(data)
        
        # Model inversion attack
        if data.attack == 'invertinggradients':
            try:
                # Setup attack using params
                cfg, setup, user, server, attacker, model, loss_fn = breaching.setup_attack(
                    attack_params=data, cfg=None, torch_model=None
                )

                # Get response channel and request token to pass into breaching
                response = request_token, queues.response_channel
                r_user_data, t_user_data, server_payload = breaching.perform_attack(
                    cfg,
                    setup,
                    user,
                    server,
                    attacker,
                    model,
                    loss_fn,
                    request_token=request_token,
                    reconstruction_frequency=data.reconstruction_frequency,
                )
                
                # Return metrics to user
                breaching.get_metrics(
                    r_user_data, t_user_data, server_payload, server, cfg, setup, response
                )

            # Report any errors to task manager
            except Exception as e:
                progress = AttackProgress(
                    message_type="error",
                    error_message=f"Attack Configuration Error: {str(e)}",
                )
                queues.response_channel.put(request_token, progress)
                # break
        elif data.attack == 'mia':
            try:
                # Perform MIA attack
                mia.perform_attack(data)
                
                    
    
# Use this for testing?
if __name__ == "__main__":
    from common import AttackParameters

    pars = AttackParameters(
        model="ResNet-18",
        datasetStructure="Foldered",
        csvPath="~/data/images",
        batchSize=1,
        numRestarts=1,
        stepSize=0.1,
        maxIterations=1,
        callbackInterval=10,
        ptFilePath="../resnet18_pretrained.pt",
        zipFilePath="../small_foldered_set.zip",
        budget=100,
        means=[0.46, 0.56, 0.57],
        stds=[0.32, 0.28, 0.27],
    )

    req_tok = str(uuid.uuid4())

    queue = WorkerCommunication()
    queue.task_channel.put(req_tok, pars)

    attack_worker(queue)
