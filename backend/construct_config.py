from typing import Optional

import breaching.breaching as breachinglib
from breaching.breaching.attacks.attack_progress import \
    AttackProgress as BreachingAttackProgress
from common import AttackParameters


class ConfigBuilder:
    def __init__(
        self,
        attack_params: AttackParameters,
    ):
        self.attack_params = attack_params

    def build(self, datasetSize: int, numClasses: int, datasetPath: Optional[str] = None):
        return self._construct_cfg(self.attack_params, datasetSize, numClasses, datasetPath)

    def _construct_cfg(
        self,
        attack_params: AttackParameters,
        datasetSize: int,
        numClasses: int,
        dataset_path=None,
    ):
        if attack_params.modality == "images":
            cfg = self._construct_images_cfg(attack_params)
        elif attack_params.modality == "text":
            cfg = self._construct_text_cfg(attack_params)
        else:
            raise TypeError(
                f"Data type of attack: {attack_params.modality} does not match anything."
            )

        assert attack_params is not None

        # setup all customisable parameters
        cfg.case.model = attack_params.model
        cfg.case.data.size = datasetSize
        cfg.case.data.classes = numClasses
        
        if dataset_path is None:
            cfg.case.data.path = "dataset"
        else:
            cfg.case.data.path = dataset_path

        if attack_params.datasetStructure == "CSV":
            cfg.case.data.name = "CustomCsv"
        elif attack_params.datasetStructure == "Foldered":
            cfg.case.data.name = "CustomFolders"
        if attack_params.datasetStructure == "text":
            cfg.case.data = breachinglib.get_config(
                overrides=["case=10_causal_lang_training", "attack=tag"]
            ).case.data
            cfg.case.data.path = "~/data"
            print("defaulted to wikitext")
            cfg.case.data.shape = attack_params.shape
        else:
            print("Could not match dataset structure")
            if attack_params.modality == "images":
                cfg.case.data = breachinglib.get_config(
                    overrides=["case/data=CIFAR10"]
                ).case.data
                print("defaulted to CIFAR10")
            elif attack_params.modality == "text":
                cfg.case.data = breachinglib.get_config(
                    overrides=["case/data=wikitext"]
                ).case.data
                cfg.case.data.path = "~/data"
                print("defaulted to wikitext")
            else:
                raise TypeError(
                    f"Data type of attack: {attack_params.modality} does not match anything."
                )

        if dataset_path == None:
            cfg.case.data.path = "dataset"
        else:
            cfg.case.data.path = dataset_path

        if any(attack_params.means) and any(attack_params.stds):
            cfg.case.data.mean = attack_params.means
            cfg.case.data.std = attack_params.stds
            cfg.case.data.normalize = False

        cfg.case.data.batch_size = attack_params.batchSize
        cfg.attack.optim.step_size = attack_params.stepSize
        cfg.attack.optim.max_iterations = attack_params.maxIterations

        cfg.attack.optim.callback = attack_params.callbackInterval
        cfg.case.user.user_idx = attack_params.user_idx
        cfg.case.data.default_clients = attack_params.number_of_clients
        # cfg.attack.optim.callback = 1
        # cfg.case.user.user_idx = random.randint(0, cfg.case.data.default_clients - 1)

        cfg.attack.restarts.num_trials = attack_params.numRestarts

        return cfg

    def _construct_text_cfg(self, attack_params: AttackParameters):
        if attack_params.attack == "TAG":
            cfg = breachinglib.get_config(
                overrides=["case=10_causal_lang_training", "attack=tag"]
            )
        else:
            raise TypeError(f"No text attack match; {attack_params.attack}")

        if attack_params.model == "bert":
            cfg.case.model = "bert-base-uncased"
        elif attack_params.model == "gpt2":
            cfg.case.model = "gpt2"
        elif attack_params.model == "transformer3":
            cfg.case.model = "transformer3"
        else:
            try:
                assert (
                    attack_params.model
                    in {
                        # ... list of all supported models
                    }
                )
                cfg.case.model = attack_params.model
            except AssertionError as a:
                raise TypeError(f"no model match for text: {attack_params.model}")

        if attack_params.tokenizer == "bert":
            cfg.case.data.tokenizer = "bert-base-uncased"
            cfg.case.data.task = "masked-lm"
            cfg.case.data.vocab_size = 30522
            cfg.case.data.mlm_probability = 0.15
        elif attack_params.tokenizer == "gpt2":
            cfg.case.model = "gpt2"
            cfg.case.data.task = "causal-lm"
            cfg.case.data.vocab_size = 50257
        elif attack_params.tokenizer == "transformer3":
            cfg.case.model = "transformer3"
        else:
            raise TypeError(f"no model match for tokenizer: {attack_params.model}")

        cfg.case.data.shape = attack_params.shape
        cfg.case.data.modality = "text"

        return cfg

    def _construct_images_cfg(self, attack_params: AttackParameters):
        if attack_params.attack == "invertinggradients":
            cfg = breachinglib.get_config()
            cfg.case.data.partition = "random"
            # default case.model=ResNet18
        elif attack_params.attack == "modern":
            cfg = breachinglib.get_config(overrides=["attack=modern"])
            cfg.case.data.partition = "unique-class"
            cfg.attack.regularization.deep_inversion.scale = 1e-4
        elif attack_params.attack == "fishing_for_user_data":
            cfg = breachinglib.get_config(
                overrides=[
                    "case/server=malicious-fishing",
                    "attack=clsattack",
                    "case/user=multiuser_aggregate",
                ]
            )
            cfg.case.user.user_range = [0, 1]
            cfg.case.data.partition = "random"  # This is the average case
            cfg.case.user.num_data_points = 256
            cfg.case.data.default_clients = 32
            cfg.case.user.provide_labels = True  # Mostly out of convenience
            cfg.case.server.target_cls_idx = 0  # Which class to attack?
        # Less important attacks
        elif attack_params.attack == "analytic":
            cfg = breachinglib.get_config(
                overrides=["attack=analytic", "case.model=linear"]
            )
            cfg.case.data.partition = "balanced"
            cfg.case.data.default_clients = 50
            cfg.case.user.num_data_points = 256  # User batch size
        elif attack_params.attack == "rgap":
            cfg = breachinglib.get_config(
                overrides=[
                    "attack=rgap",
                    "case.model=cnn6",
                    "case.user.provide_labels=True",
                ]
            )
            cfg.case.user.num_data_points = 1
        elif attack_params.attack == "april_analytic":
            cfg = breachinglib.get_config(
                overrides=["attack=april_analytic", "case.model=vit_small_april"]
            )
            cfg.case.data.partition = "unique-class"
            cfg.case.user.num_data_points = 1
            cfg.case.server.pretrained = True
            cfg.case.user.provide_labels = False
        elif attack_params.attack == "deepleakage":
            cfg = breachinglib.get_config(
                overrides=["attack=deepleakage", "case.model=ConvNet"]
            )
            cfg.case.data.partition = "unique-class"
            cfg.case.user.provide_labels = False

        cfg.case.data.classes = attack_params.numClasses
        cfg.case.data.mean = attack_params.means
        cfg.case.data.std = attack_params.stds
        cfg.case.data.modality = "images"
        return cfg
