from common import AttackParameters
import breaching.breaching as breachinglib
import random


class ConfigBuilder:
    def __init__(self, attack_params: AttackParameters) -> None:
        self.attack_params=attack_params

    def build(self):
        return self._construct_cfg(self.attack_params)
    
    def _construct_cfg(
        self,
        attack_params: AttackParameters,
        dataset_path=None,
    ):
        print("constructing")
        match attack_params.breaching_params.modality:
            
            case "images":
                cfg = self._construct_images_cfg(attack_params)
            case "text":
                cfg = self._construct_text_cfg(attack_params)
            case _:
                raise TypeError(
                    f"Data type of attack: {attack_params.breaching_params.modality} does not match anything."
                )
        assert attack_params is not None
        print("done")
        
        # setup all customisable parameters
        cfg.case.model = attack_params.model
        match attack_params.breaching_params.datasetStructure:
            case "CSV":
                cfg.case.data.name = "CustomCsv"
            case "Foldered":
                cfg.case.data.name = "CustomFolders"
            case _:
                print("Could not match dataset structure")
                match attack_params.breaching_params.modality:
                    case "images":
                        cfg.case.data = breachinglib.get_config(
                            overrides=["case/data=CIFAR10"]
                        ).case.data
                        print("defaulted to CIFAR10")
                    case "text":
                        cfg.case.data = breachinglib.get_config(
                            overrides=["case/data=wikitext"]
                        ).case.data
                        print("defaulted to wikitext")
                    case _:
                        raise TypeError(
                            f"Data type of attack: {attack_params.breaching_params.modality} does not match anything."
                        )
        print("data")
        match dataset_path:
            case None:
                cfg.case.data.path = "dataset"
            case _:
                cfg.case.data.path = dataset_path

        if any(attack_params.breaching_params.means) and any(attack_params.breaching_params.stds):
            cfg.case.data.mean = attack_params.breaching_params.means
            cfg.case.data.std = attack_params.breaching_params.stds
            cfg.case.data.normalize = False

        cfg.case.user.num_data_points = attack_params.breaching_params.batchSize
        cfg.attack.optim.step_size = attack_params.breaching_params.stepSize
        cfg.attack.optim.max_iterations = attack_params.breaching_params.maxIterations
        cfg.attack.optim.callback = 1
        cfg.case.user.user_idx = random.randint(0, cfg.case.data.default_clients - 1)
        cfg.attack.restarts.num_trials = attack_params.breaching_params.numRestarts

        return cfg

    def _construct_text_cfg(self, attack_params: AttackParameters):
        match attack_params.attack:
            case "TAG":
                cfg = breachinglib.get_config(overrides=["attack=tag"])
            case _:
                raise TypeError(f"No text attack match; {attack_params.attack}")

        match attack_params.model:
            case "bert":
                cfg.case.model = "bert-base-uncased"
            case "gpt2":
                cfg.case.model = "gpt2"
            case "transformer3":
                cfg.case.model = "transformer3"
            case _:
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

        match attack_params.tokenizer:
            case "bert":
                cfg.case.data.tokenizer = "bert-base-uncased"
                cfg.case.data.task = "masked-lm"
                cfg.case.data.vocab_size = 30522
                cfg.case.data.mlm_probability = 0.15
            case "gpt2":
                cfg.case.model = "gpt2"
                cfg.case.data.task = "causal-lm"
                cfg.case.data.vocab_size = 50257
            case "transformer3":
                cfg.case.model = "transformer3"
            case _:
                raise TypeError(f"no model match for tokenizer: {attack_params.model}")

        cfg.case.data.shape = attack_params.shape
        return cfg

    def _construct_images_cfg(self, attack_params: AttackParameters):
        match attack_params.attack:
            case "invertinggradients":
                cfg = breachinglib.get_config()
                cfg.case.data.partition = "random"
                # default case.model=ResNet18
            case "modern":
                cfg = breachinglib.get_config(overrides=["attack=modern"])
                cfg.case.data.partition = "unique-class"
                cfg.attack.regularization.deep_inversion.scale = 1e-4
            case "fishing_for_user_data":
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
            case "analytic":
                cfg = breachinglib.get_config(
                    overrides=["attack=analytic", "case.model=linear"]
                )
                cfg.case.data.partition = "balanced"
                cfg.case.data.default_clients = 50
                cfg.case.user.num_data_points = 256  # User batch size
            case "rgap":
                cfg = breachinglib.get_config(
                    overrides=[
                        "attack=rgap",
                        "case.model=cnn6",
                        "case.user.provide_labels=True",
                    ]
                )
                cfg.case.user.num_data_points = 1
            case "april_analytic":
                cfg = breachinglib.get_config(
                    overrides=["attack=april_analytic", "case.model=vit_small_april"]
                )
                cfg.case.data.partition = "unique-class"
                cfg.case.user.num_data_points = 1
                cfg.case.server.pretrained = True
                cfg.case.user.provide_labels = False
            case "deepleakage":
                cfg = breachinglib.get_config(
                    overrides=["attack=deepleakage", "case.model=ConvNet"]
                )
                cfg.case.data.partition = "unique-class"
                cfg.case.user.provide_labels = False
        return cfg
    