export const getAttacksInfo = () => {
  let info = "Select the attack to be performed.";
  info +=
    "\n\n<strong>Inverting Gradients</strong>: Uses the gradient updates of the target model to invert an image to a target class.";
  info +=
    "\n\n<strong>TAG</strong>: Uses the model to generate a target sequence of tokens.";
  info +=
    "\n\n<strong>Membership Inference</strong>: Performs likelihood-ratio test to determine if a given data point was used to train the model.";
  return info;
};

export const getPtFileInfo = (attack: string) => {
  let info =
    "Upload a .pt file (PyTorch State Dictionary). This must match the selected model.";
  if (attack === "invertinggradients" || attack === "tag") {
    info += "\n\nTo attack an untrained model leave this field empty.";
  }
  return info;
};

export const getZipFileInfo = (attack: string) => {
  if (attack === "mia") {
    return "";
  } else {
    return "Upload a .zip file containing the custom dataset to be used in the attack.\n\nIt should be organised as follows:\n\n dataset\n ├── class1\n │   ├── img1.jpg\n │   ├── img2.jpg\n │   └── ...\n └── class2\n     ├── img1.jpg\n     ├── img2.jpg\n     └── ...";
  }
};

export const getDatasetParamsInfo = (attack: string) => {
  let info = "Parameters of the uploaded dataset to be used in the attack.";
  switch (attack) {
    case "invertinggradients":
      info +=
        "\n\n<strong>Mean, Standard Deviation</strong>: The mean and standard deviation of the images in the dataset. Inferred from the dataset if left empty.";
      info +=
        "\n\n<strong>Batch Size</strong>: Number of images per batch. Each batch is computed in a grid.";
      break;
    case "tag":
      info +=
        "\n\n<strong>Text Dataset</strong>: The dataset to be used in the attack.";
      info +=
        "\n\n<strong>Tokenizer</strong>: Used to preprocess text data before feeding into the model.";
      info +=
        "\n\n<strong>No. Data Points</strong>: The number of sentences selected from the dataset.";
      info +=
        "\n\n<strong>Sequence Length</strong>: The number of tokens in a sequence.";
      break;
  }

  return info;
};

export const getAttackParamsInfo = () => {
  let info = "Parameters of the attack to be performed.";
  info +=
    "\n\n<strong>No. Restarts</strong>: The number of times the attack restarts from the beginning.";
  info += "\n\n<strong>Step Size</strong>: Attack learning rate.";
  info +=
    "\n\n<strong>Max Iterations</strong>: The number of iterations run per restart.";
  return info;
};
