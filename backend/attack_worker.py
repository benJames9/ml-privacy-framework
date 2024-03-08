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
import traceback
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
    mia = MiaAdapter(queues.response_channel)

    # Permenantly loop, fetching data from queues
    while True:
        print("waiting for data...")
        request_token, data = queues.task_channel.get()
        print(data)

        try:
            # Model inversion attack
            if data.attack == "invertinggradients":
                # Setup attack using params
                cfg, setup, user, server, attacker, model, loss_fn = (
                    breaching.setup_attack(attack_params=data, cfg=None)
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
                    reconstruction_frequency=data.breaching_params.reconstruction_frequency,
                )

                # Return metrics to user
                breaching.get_metrics(
                    r_user_data,
                    t_user_data,
                    server_payload,
                    server,
                    cfg,
                    setup,
                    response,
                )

            elif data.attack == "mia":
                # Perform MIA attack
                mia.perform_attack(data, request_token)

            else:
                raise ValueError(f"Attack type {data.attack} not supported")

        # Report any errors to task manager
        except Exception as e:
            print(f"Attack worker exception was:\n{e}")
            traceback.print_exc()
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
        attack="TAG",
        model="gpt2",
        modality="text",
        datasetStructure="text",
        csvPath=None,
        batchSize=2,
        numRestarts=1,
        stepSize=0.5,
        maxIterations=100,
        callbackInterval=10,
        ptFilePath=None,
        zipFilePath="../small_foldered_set.zip",
        budget=100,
        means=[],
        stds=[],
    )

    req_tok = str(uuid.uuid4())

    queue = WorkerCommunication()
    queue.task_channel.put(req_tok, pars)

    attack_worker(queue)
