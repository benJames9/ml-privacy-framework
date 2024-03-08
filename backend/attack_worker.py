import base64
import traceback
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

def clear_attack_images():
    # Clear attack_images folder
    attack_images_folder = './attack_images/'
    for filename in os.listdir(attack_images_folder):
        file_path = os.path.join(attack_images_folder, filename)
        os.remove(file_path)


# Attack worker function to run on separate process and complete attacks
def attack_worker(queues: WorkerCommunication):
    """
    This shows how the worker process should be structured.
    The actual worker should receive the data from the input_queue,
      and run the attack with the given parameters.
    """
    
    # Initialise adapters for different attacks
    breaching = BreachingAdapter(queues.response_channel)
    mia = MiaAdapter(queues.response_channel)

    # Clear attack_images folder
    clear_attack_images()
    
    # Permenantly loop, fetching data from queues
    while True:
        print("waiting for data...")
        request_token, data = queues.task_channel.get()
        print(data)

        # Clear attack_images folder
        clear_attack_images()

        try:
            # Model inversion attack
            if data.attack == 'invertinggradients':
                # Setup attack using params
                setup, model, permutation_arr, builder = breaching.setup_attack(
                    attack_params=data, cfg=None, torch_model=None
                )

                # Get response channel and request token to pass into breaching
                response = request_token, queues.response_channel
                num_batches, metrics_arr, cfg = breaching.perform_batches(
                    builder,
                    setup, 
                    model, 
                    request_token, 
                    data.breaching_params.reconstruction_frequency, 
                    permutation_arr
                )
                # r_user_data, t_user_data, server_payload = breaching.perform_attack(
                #     cfg,
                #     setup,
                #     user,
                #     server,
                #     attacker,
                #     model,
                #     loss_fn,
                #     request_token=request_token,
                #     reconstruction_frequency=data.breaching_params.reconstruction_frequency,
                # )
                
                # Return metrics to user
                breaching.get_metrics(
                    num_batches, metrics_arr, cfg, response
                )

            elif data.attack == 'mia':
                # Perform MIA attack
                mia.perform_attack(data, request_token)
            
            else:
                raise ValueError(f"Attack type {data.attack} not supported")
                
            
        # Report any errors to task manager 
        except Exception as e:
            progress = AttackProgress(
                message_type="error",
                error_message=f"Attack Configuration Error: {str(e)}",
            )
            traceback.print_exc()
            queues.response_channel.put(request_token, progress)
                
                    
    
# Use this for testing?
if __name__ == "__main__":
    from common import AttackParameters

    pars = AttackParameters(
        model='AlexNet',
        datasetStructure='Foldered',
        csvPath=None,
        batchSize=1,
        numRestarts=1,
        stepSize=0.1,
        maxIterations=1,
        callbackInterval=10,
        ptFilePath=None,
        zipFilePath='../small_foldered_set.zip',
        budget=100,
        means=[],
        stds=[]
    )

    req_tok = str(uuid.uuid4())

    queue = WorkerCommunication()
    queue.task_channel.put(req_tok, pars)

    attack_worker(queue)
