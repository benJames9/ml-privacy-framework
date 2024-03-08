from common import AttackParameters
import breaching.breaching as breachinglib
import random


class ConfigBuilder:
    def __init__(self, attack_params: AttackParameters) -> None:
        self.attack_params = attack_params

    def build(self):
        return self._construct_cfg(self.attack_params)

    def _construct_cfg(self, attack_params: AttackParameters, dataset_path=None):
        print("here")
        if attack_params.modality == "images":
            cfg = self._construct_images_cfg(attack_params)
        elif attack_params.modality == "text":
            cfg = self._construct_text_cfg(attack_params)
        else:
            raise TypeError(
                f"Data type of attack: {attack_params.modality} does not match anything."
            )

        assert attack_params is not None
        print("done")

        # setup all customisable parameters
        cfg.case.model = attack_params.model

        if attack_params.zipFilePath is None and attack_params.modality == "images":
            attack_params.datasetStructure = "default"
            print("defaulting")

        if dataset_path == None:
            cfg.case.data.path = "dataset"
        else:
            cfg.case.data.path = dataset_path

        print(attack_params.modality)
        if attack_params.datasetStructure == "CSV":
            cfg.case.data.name = "CustomCsv"
        elif attack_params.datasetStructure == "Foldered":
            cfg.case.data.name = "CustomFolders"
        else:
            if attack_params.modality == "images":
                cfg.case.data = breachinglib.get_config(
                    overrides=["case/data=CIFAR10"]
                ).case.data
                print("defaulted to CIFAR10")
                # cfg.case.data.
            elif attack_params.modality == "text":
                cfg.case.data = breachinglib.get_config(
                    overrides=["case/data=wikitext"]
                ).case.data
                print("defaulted to wikitext")
                cfg = self._construct_text_model_cfg(attack_params.model, cfg)
                cfg = self._construct_text_tokenizer_cfg(attack_params.tokenizer, cfg)
                cfg.case.data.shape = attack_params.shape
            else:
                print("Could not match dataset structure")
                raise TypeError(
                    f"Data type of attack: {attack_params.modality} does not match anything."
                )

        if any(attack_params.means) and any(attack_params.stds):
            cfg.case.data.mean = attack_params.means
            cfg.case.data.std = attack_params.stds
            cfg.case.data.normalize = False

        cfg.case.user.num_data_points = attack_params.batchSize
        cfg.attack.optim.step_size = attack_params.stepSize
        cfg.attack.optim.max_iterations = attack_params.maxIterations
        cfg.attack.optim.callback = 1
        cfg.case.user.user_idx = random.randint(0, cfg.case.data.default_clients - 1)
        cfg.attack.restarts.num_trials = attack_params.numRestarts
        return cfg

    def _construct_text_cfg(self, attack_params: AttackParameters):
        if attack_params.attack.lower() == "tag":
            cfg = breachinglib.get_config(
                overrides=["case=10_causal_lang_training", "attack=tag"]
            )
        else:
            raise TypeError(f"No text attack match; {attack_params.attack}")
        cfg = self._construct_text_model_cfg(attack_params.model, cfg)
        cfg = self._construct_text_tokenizer_cfg(attack_params.tokenizer, cfg)
        cfg.case.data.shape = attack_params.shape
        return cfg

    def _construct_text_model_cfg(self, model, cfg):
        model = model.lower()
        if model == "bert":
            cfg.case.model = "BertModel"
        elif model == "gpt2":
            cfg.case.model = "gpt2"
        elif model == "transformer3":
            cfg.case.model = "transformer3"
        else:
            try:
                assert (
                    model
                    in {
                        # ... list of all supported models
                    }
                )
                cfg.case.model = model
            except AssertionError as a:
                raise TypeError(f"no model match for text: {model}")
        return cfg

    def _construct_text_tokenizer_cfg(self, tokenizer, cfg):
        tokenizer = tokenizer.lower()
        if tokenizer == "bert":
            cfg.case.data.tokenizer = "bert-base-uncased"
            cfg.case.data.task = "masked-lm"
            cfg.case.data.vocab_size = 30522
            cfg.case.data.mlm_probability = 0.15
        elif tokenizer == "gpt2":
            cfg.case.data.tokenizer = "gpt2"
            cfg.case.data.task = "causal-lm"
            cfg.case.data.vocab_size = 50257
        else:
            cfg.case.data.tokenizer = tokenizer
        return cfg

    def _construct_images_cfg(self, attack_params: AttackParameters):
        if attack_params.attack == "invertinggradients":
            cfg = breachinglib.get_config()
            cfg.case.data.partition = "random"
            cfg.case.data.default_clients = 50
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

        return cfg
