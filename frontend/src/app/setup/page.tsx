"use client";
import { useEffect, useState } from "react";
import DatasetParams from "@/components/DatasetParams";
import FileUpload from "@/components/FileUpload";
import HBar from "@/components/HBar";
import ModelSelect from "@/components/ModelSelect";
import Navbar from "@/components/Navbar";
import AttackParams from "@/components/AttackParams";
import EvaluateButton from "@/components/EvaluateButton";
import AttackSelect from "@/components/AttackSelect";
import LoadingIcon from "@/components/LoadingIcon";
import ErrorAlert from "@/components/ErrorAlert";
import InfoPopup from "@/components/InfoPopup";
import MiaParams from "@/components/MiaParams";

export default function SetupPage() {
  const imageModels: string[] = ["ResNet-18", "DenseNet-121", "VGG-16", "AlexNet"];
  const textModels: string[] = ["LSTM", "Transformer3", "Transformer31", "Linear"];
  const miaModels: string[] = ["ResNet-18"];
  const attacks: string[] = ["Inverting Gradients\n(Single Step)", "TAG\n(Text Attack)", "Fishing for\nUser Data", "Membership\nInference"];
  const textDatasets: string[] = ["CoLA", "Random Tokens", "Stack Overflow", "WikiText"]
  const tokenizers: string[] = ["GPT-2", "BERT", "Transformer3"];

  const [model, setSelectedModel] = useState<string>("");
  const [attack, setSelectedAttack] = useState<string>("");
  const [modality, setModality] = useState<"images" | "text">("images");

  const [ptFile, setSelectedPtFile] = useState<File | null>(null);
  const [zipFile, setSelectedZipFile] = useState<File | null>(null);

  // Image parameters
  const [batchSize, setBatchSize] = useState<number>(0);
  const [mean, setMean] = useState<[number, number, number]>([0, 0, 0]);
  const [std, setStd] = useState<[number, number, number]>([0, 0, 0]);

  // Text parameters
  const [textDataset, setTextDataset] = useState<string>(textDatasets[0]);
  const [textDataPoints, setTextDataPoints] = useState<number>(0);
  const [seqLength, setSeqLength] = useState<number>(0);
  const [tokenizer, setTokenizer] = useState<string>(tokenizers[0]);

  // Attack parameters
  const [numRestarts, setNumRestarts] = useState<number>(0);
  const [stepSize, setStepSize] = useState<number>(0);
  const [maxIterations, setMaxIterations] = useState<number>(0);

  // MIA parameters
  const [labelDict, setLabelDict] = useState<File | null>(null);
  const [targetImage, setTargetImage] = useState<File | null>(null);
  const [targetLabel, setTargetLabel] = useState<string>("");
  const [numShadowModels, setNumShadowModels] = useState<number>(0);
  const [numDataPoints, setNumDataPoints] = useState<number>(0);
  const [numEpochs, setNumEpochs] = useState<number>(0);
  const [shadowBatchSize, setShadowBatchSize] = useState<number>(0);
  const [learningRate, setLearningRate] = useState<number>(0);

  const [submitted, setSubmitted] = useState<boolean>(false);
  const [isInvalid, setIsInvalid] = useState<boolean>(false);
  const [errors, setErrors] = useState<string[]>([]);

  useEffect(() => {
    // Scroll to loading icon
    if (submitted) {
      const loadingIcon = document.getElementById("loading-icon");
      loadingIcon!.scrollIntoView({ behavior: "smooth" });
    }
  }, [submitted]);

  useEffect(() => {
    // Scroll to error alert
    if (isInvalid) {
      const errorAlert = document.getElementById("error-alert");
      errorAlert!.scrollIntoView({ behavior: "smooth" });
    }
  }, [isInvalid]);

  const invalidNum: (num: number) => boolean = (num) => {
    return num <= 0 || isNaN(num);
  }

  const isValidInput: () => boolean = () => {
    let errorMsgs: string[] = [];
    if (attack === "") {
      errorMsgs.push("Please select an attack");
    }
    if (model === "") {
      errorMsgs.push("Please select a model");
    }

    switch (attack) {
      case "invertinggradients":
        if (!zipFile) {
          errorMsgs.push("Please upload a dataset file");
        }
        if (invalidNum(batchSize)) {
          errorMsgs.push("Please enter a batch size > 0");
        }
        if (invalidNum(numRestarts)) {
          errorMsgs.push("Please enter a number of restarts > 0");
        }
        if (invalidNum(stepSize)) {
          errorMsgs.push("Please enter a step size > 0");
        }
        if (invalidNum(maxIterations)) {
          errorMsgs.push("Please enter a maximum number of iterations > 0");
        }
        if ((mean.some(val => !invalidNum(val)) || std.some(val => !invalidNum(val)))
          && (mean.some(val => invalidNum(val) || std.some(val => invalidNum(val))))) {
          errorMsgs.push("Please either enter all values for mean and std or none");
        }
        break;
      case "tag":
        if (!ptFile) {
          errorMsgs.push("Please upload a model parameters file");
        }
        if (!textDataset) {
          errorMsgs.push("Please select a text dataset");
        }
        if (!tokenizer) {
          errorMsgs.push("Please select a tokenizer");
        }
        if (invalidNum(textDataPoints)) {
          errorMsgs.push("Please enter a number of data points > 0");
        }
        if (invalidNum(seqLength)) {
          errorMsgs.push("Please enter a sequence length > 0");
        }
        if (invalidNum(numRestarts)) {
          errorMsgs.push("Please enter a number of restarts > 0");
        }
        if (invalidNum(stepSize)) {
          errorMsgs.push("Please enter a step size > 0");
        }
        if (invalidNum(maxIterations)) {
          errorMsgs.push("Please enter a maximum number of iterations > 0");
        }
        break;
      case "fishing":
        break;
      case "mia":
        if (!ptFile) {
          errorMsgs.push("Please upload a model parameters file");
        }
        if (!zipFile) {
          errorMsgs.push("Please upload a data distribution file");
        }
        if (!labelDict) {
          errorMsgs.push("Please upload a label dictionary file");
        }
        if (!targetImage) {
          errorMsgs.push("Please upload a target image file");
        }
        if (targetLabel === "") {
          errorMsgs.push("Please enter a target label");
        }
        if (invalidNum(numShadowModels) || numShadowModels < 4 || numShadowModels % 2 !== 0) {
          errorMsgs.push("Please enter an even number of shadow models >= 4");
        }
        if (invalidNum(numDataPoints)) {
          errorMsgs.push("Please enter a number of data points > 0");
        }
        if (invalidNum(numEpochs)) {
          errorMsgs.push("Please enter a number of epochs > 0");
        }
        if (invalidNum(shadowBatchSize)) {
          errorMsgs.push("Please enter a shadow batch size > 0");
        }
        if (invalidNum(learningRate)) {
          errorMsgs.push("Please enter a learning rate > 0");
        }
        break;
      default:
        break;
    }

    setErrors(errorMsgs);
    return errorMsgs.length === 0;
  }

  const onClick = async () => {
    const formData = new FormData();

    // Append files to formData
    if (ptFile) formData.append("ptFile", ptFile);
    if (zipFile) formData.append("zipFile", zipFile);

    if (!isValidInput()) {
      setSubmitted(false);
      setIsInvalid(true);
      return;
    }

    setIsInvalid(false);

    // Append text fields to formData
    formData.append("model", model);
    formData.append("attack", attack);
    formData.append("modality", modality);

    switch (attack) {
      case "invertinggradients":
        formData.append("mean", JSON.stringify(mean));
        formData.append("std", JSON.stringify(std));
        formData.append("batchSize", batchSize.toString());
        formData.append("numRestarts", numRestarts.toString());
        formData.append("stepSize", stepSize.toString());
        formData.append("maxIterations", maxIterations.toString());
        break;
      case "tag":
        formData.append("textDataset", textDataset);
        formData.append("textDataPoints", textDataPoints.toString());
        formData.append("seqLength", seqLength.toString());
        formData.append("tokenizer", tokenizer);
        formData.append("numRestarts", numRestarts.toString());
        formData.append("stepSize", stepSize.toString());
        formData.append("maxIterations", maxIterations.toString());
        break;
      case "fishing":
        break;
      case "mia":
        formData.append("labelDict", labelDict!);
        formData.append("targetImage", targetImage!);
        formData.append("targetLabel", targetLabel);
        formData.append("numShadowModels", numShadowModels.toString());
        formData.append("numDataPoints", numDataPoints.toString());
        formData.append("numEpochs", numEpochs.toString());
        formData.append("shadowBatchSize", shadowBatchSize.toString());
        formData.append("learningRate", learningRate.toString());
        break;
      default:
        break;
    }

    const res = await fetch("/api/submit-attack", {
      method: 'POST',
      body: formData,
    })

    const req_token = await res.json();
    window.location.href = `/results/${req_token}`;
  }

  const handlePtFileChange = (file: File | null) => {
    setSelectedPtFile(file);
  }

  const handleZipFileChange = (file: File | null) => {
    setSelectedZipFile(file);
  }

  const handleDataParamsChange = (field: string, value: string) => {
    switch (field) {
      case "batchSize":
        setBatchSize(parseInt(value));
        break;
      case "mean1":
        setMean([parseFloat(value) || 0, mean[1], mean[2]]);
        break;
      case "mean2":
        setMean([mean[0], parseFloat(value) || 0, mean[2]]);
        break;
      case "mean3":
        setMean([mean[0], mean[1], parseFloat(value) || 0]);
        break;
      case "std1":
        setStd([parseFloat(value) || 0, std[1], std[2]]);
        break;
      case "std2":
        setStd([std[0], parseFloat(value) || 0, std[2]]);
        break;
      case "std3":
        setStd([std[0], std[1], parseFloat(value) || 0]);
        break;
      case "textDataset":
        setTextDataset(value);
        break;
      case "textDataPoints":
        setTextDataPoints(parseInt(value));
        break;
      case "seqLength":
        setSeqLength(parseInt(value));
        break;
      case "tokenizer":
        setTokenizer(value);
        break;
      default:
        break;
    }
  }

  const handleAttackParamsChange = (field: string, value: string) => {
    switch (field) {
      case "restarts":
        setNumRestarts(parseInt(value));
        break;
      case "stepSize":
        setStepSize(parseFloat(value));
        break;
      case "maxIterations":
        setMaxIterations(parseInt(value));
        break;
      default:
        break;
    }
  }

  const handleMiaParamsChange = (field: string, value: string | (File | null)) => {
    switch (field) {
      case "labelDict":
        setLabelDict(value as File);
        break;
      case "targetImage":
        setTargetImage(value as File);
        break;
      case "targetLabel":
        setTargetLabel(value as string);
        break;
      case "numShadowModels":
        setNumShadowModels(parseInt(value as string));
        break;
      case "numDataPoints":
        setNumDataPoints(parseInt(value as string));
        break;
      case "numEpochs":
        setNumEpochs(parseInt(value as string));
        break;
      case "shadowBatchSize":
        setShadowBatchSize(parseInt(value as string));
        break;
      case "learningRate":
        setLearningRate(parseFloat(value as string));
        break;
      default:
        break;
    }
  }

  const onAttackSelect = (attack: string) => {
    switch (attack) {
      case "Inverting Gradients\n(Single Step)":
        setSelectedAttack("invertinggradients");
        setModality("images");
        break;
      case "TAG\n(Text Attack)":
        setSelectedAttack("tag");
        setModality("text");
        break;
      case "Fishing for\nUser Data":
        setSelectedAttack("fishing");
        setModality("images");
        break;
      case "Membership\nInference":
        setSelectedAttack("mia");
        setModality("images");
        break;
      default:
        break;
    }
  }

  const getDatasetParamsInfo = () => {
    let info = "Enter the parameters of the uploaded dataset to be used in the attack.";
    switch (attack) {
      case "invertinggradients":
        info += "\n\n<strong>Mean, Standard Deviation</strong>: The mean and standard deviation of the images in the dataset. Inferred from the dataset if left empty.";
        break;
      case "tag":
        info += "\n\n<strong>Text Dataset</strong>: The dataset to be used in the attack.";
        info += "\n\n<strong>No. Data Points</strong>: The number of data points in the dataset. Inferred from the dataset if left empty."
        info += "\n\n<strong>Sequence Length</strong>: The length of the sequences in the dataset. Inferred from the dataset if left empty."
        break;
    }
    info += "\n\n<strong>Batch Size</strong>: The batch size to be used in the attack.";
    return info;
  }

  const getAttackParamsInfo = () => {
    let info = "Enter the parameters of the attack to be performed.";
    info += "\n\n<strong>No. Restarts</strong>: The number of times the attack restarts from the beginning.";
    info += "\n\n<strong>Step Size</strong>: Attack learning rate.";
    info += "\n\n<strong>Max Iterations</strong>: The number of iterations run per restart.";
    return info;
  }

  const getModels = () => {
    switch (attack) {
      case "tag":
        return textModels;
      case "mia":
        return miaModels;
      default:
        return imageModels;
    }
  }

  return (
    <main>
      <Navbar />
      <div className="flex min-h-screen flex-col items-center justify-between px-24 py-8 bg-gradient-to-r from-black to-blue-950">
        {/* Attack Select */}
        <h2 className="text-3xl font-bold text-gray-400 mb-8 flex items-start whitespace-pre">Select Attack <span className="text-sm text-red-500">*</span></h2>
        <AttackSelect attacks={attacks} onChange={onAttackSelect} />
        <HBar />

        {/* Model Select */}
        <div className="flex items-start">
          <h2 className="text-3xl font-bold text-gray-400 mb-8 flex items-start whitespace-pre" id="model-select-header">
            Select Model <span className="text-sm text-red-500">*</span>
          </h2>
          <InfoPopup text="Select one of our suppported models to perform the attack on." />
        </div>
        <ModelSelect
          models={getModels()}
          onChange={(model: string) => { setSelectedModel(model) }}
          nextElement={attack !== "" ? "upload-pt-header" : ""} />

        {/* Upload model parameters pt file */}
        {attack !== "" && <div className="flex flex-col items-center">
          <HBar />
          <div className="flex items-start">
            <h3 className="text-2xl font-bold text-gray-400 mb-8 flex items-start whitespace-pre" id="upload-pt-header">
              Upload Model Parameters {attack === "mia" || attack === "tag" ? <span className="text-sm text-red-500">*</span> : ""}
            </h3>
            <InfoPopup text={"Upload a .pt file (PyTorch State Dictionary). This must match the selected model."} />
          </div>
          <div className="mb-2">
            <FileUpload
              expectedFileType="pt"
              label="Select File (.pt)"
              onFileChange={handlePtFileChange}
              nextElement={attack === "invertinggradients" || attack === "mia" ? "upload-zip-header" : "data-params-header"}
            />
            {ptFile && (
              <p className="mt-2 text-sm text-gray-400">{ptFile.name}</p>
            )}
          </div>
          <HBar />
        </div>}

        {(attack === "invertinggradients" || attack === "mia") && <div className="flex flex-col items-center">
          {/* Upload zip file */}
          <div className="flex items-start justify-center">
            <h3 className="text-2xl font-bold text-gray-400 mb-8 flex items-start whitespace-pre" id="upload-zip-header">
              {attack === "mia" ? "Upload Data Distribution" : "Upload Custom Dataset"} <span className="text-sm text-red-500">*</span>
            </h3>
            <InfoPopup text={"Upload a .zip file containing the custom dataset to be used in the attack.\n\nIt should be organised as follows:\n\n dataset\n ├── class1\n │   ├── img1.jpg\n │   ├── img2.jpg\n │   └── ...\n └── class2\n     ├── img1.jpg\n     ├── img2.jpg\n     └── ..."} />
          </div>

          <div className="mb-2">
            <FileUpload
              expectedFileType="zip"
              label="Select File (.zip)"
              onFileChange={handleZipFileChange}
              nextElement={attack === "mia" ? "upload-label-dict-header" : "data-params-header"}
            />
            <div>
              {zipFile && (
                <p className="mt-2 text-sm text-gray-400">{zipFile.name}</p>
              )}
            </div>
          </div>
          <HBar />
        </div>}

        {attack === "mia" ?
          <MiaParams
            handleMiaParamsChange={handleMiaParamsChange}
            labelDict={labelDict}
            targetImage={targetImage}
          />
          : attack !== "" &&
          <div>
            {/* Dataset Parameters */}
            <div className="flex items-start justify-center">
              <h3 className="text-2xl font-bold text-gray-400 mb-4" id="data-params-header">
                Dataset Parameters
              </h3>
              <InfoPopup text={getDatasetParamsInfo()} />
            </div>
            <DatasetParams
              handleDataParamsChange={handleDataParamsChange}
              attack={attack}
              textDatasets={textDatasets}
              tokenizers={tokenizers}
            />
            <HBar />

            {/* Attack Parameters */}
            <div className="flex items-start justify-center">
              <h3 className="text-2xl font-bold text-gray-400 mb-4">
                Attack Parameters
              </h3>
              <InfoPopup text={getAttackParamsInfo()} />
            </div>
            <AttackParams handleAttackParamsChange={handleAttackParamsChange} />
          </div>
        }

        <EvaluateButton onClick={() => {
          if (!submitted) {
            setSubmitted(true);
            onClick();
          }
        }} />
        <div id="loading-icon">
          {submitted && <LoadingIcon />}
        </div>
        <div id="error-alert">
          {isInvalid && <ErrorAlert errors={errors} />}
        </div>
      </div>
    </main>
  )
}
