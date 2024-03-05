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

export default function SetupPage() {
  const imageModels: string[] = ["ResNet-18", "DenseNet-121", "VGG-16", "AlexNet"];
  const textModels: string[] = ["LSTM", "Transformer3", "Transformer31", "Linear"];
  const attacks: string[] = ["Inverting Gradients\n(Single Step)", "TAG\n(Text Attack)"]

  const [model, setSelectedModel] = useState<string>("");
  const [attack, setSelectedAttack] = useState<string>("");

  const [ptFile, setSelectedPtFile] = useState<File | null>(null);
  const [zipFile, setSelectedZipFile] = useState<File | null>(null);

  // Dataset parameters
  const [datasetStructure, setDatasetStructure] = useState<"Foldered" | "CSV">("Foldered");
  const [csvPath, setCsvPath] = useState<string>("");
  const [batchSize, setBatchSize] = useState<number>(0);
  const [imageShape, setImageShape] = useState<[number, number, number]>([0, 0, 0]);
  const [mean, setMean] = useState<[number, number, number]>([0, 0, 0]);
  const [std, setStd] = useState<[number, number, number]>([0, 0, 0]);

  // Attack parameters
  const [numRestarts, setNumRestarts] = useState<number>(0);
  const [stepSize, setStepSize] = useState<number>(0);
  const [maxIterations, setMaxIterations] = useState<number>(0);
  const [budget, setBudget] = useState<number>(0);

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
    if (!ptFile) {
      errorMsgs.push("Please upload a model parameter file");
    }
    if (attack === "Inverting Gradients\n(Single Step)" && !zipFile) {
      errorMsgs.push("Please upload a dataset file");
    }
    if (datasetStructure === "CSV" && csvPath === "") {
      errorMsgs.push("Please enter the path to the CSV file");
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
    if (invalidNum(budget)) {
      errorMsgs.push("Please enter a budget > 0");
    }
    if ((mean.some(val => !invalidNum(val)) || std.some(val => !invalidNum(val)))
      && (mean.some(val => invalidNum(val) || std.some(val => invalidNum(val))))) {
      errorMsgs.push("Please either enter all values for mean and std or none");
    }
    if (imageShape.some(val => invalidNum(val)) && imageShape.some(val => !invalidNum(val))) {
      errorMsgs.push("Please either enter all values for image shape or none");
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
    formData.append("datasetStructure", datasetStructure);
    formData.append("csvPath", csvPath);
    formData.append("mean", JSON.stringify(mean));
    formData.append("std", JSON.stringify(std));
    formData.append("batchSize", batchSize.toString());
    formData.append("numRestarts", numRestarts.toString());
    formData.append("stepSize", stepSize.toString());
    formData.append("maxIterations", maxIterations.toString());
    formData.append("budget", budget.toString());

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

  const handleStructureChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setDatasetStructure(e.target.value as "Foldered" | "CSV");
  }

  const handleDataParamsChange = (field: string, value: string) => {
    switch (field) {
      case "csvPath":
        setCsvPath(value);
        break;
      case "batchSize":
        setBatchSize(parseInt(value));
        break;
      case "imageShape1":
        setImageShape([parseInt(value), imageShape[1], imageShape[2]]);
        break;
      case "imageShape2":
        setImageShape([imageShape[0], parseInt(value), imageShape[2]]);
        break;
      case "imageShape3":
        setImageShape([imageShape[0], imageShape[1], parseInt(value)]);
        break;
      case "mean1":
        setMean([parseFloat(value), mean[1], mean[2]]);
        break;
      case "mean2":
        setMean([mean[0], parseFloat(value), mean[2]]);
        break;
      case "mean3":
        setMean([mean[0], mean[1], parseFloat(value)]);
        break;
      case "std1":
        setStd([parseFloat(value), std[1], std[2]]);
        break;
      case "std2":
        setStd([std[0], parseFloat(value), std[2]]);
        break;
      case "std3":
        setStd([std[0], std[1], parseFloat(value)]);
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
      case "budget":
        setBudget(parseInt(value));
        break;
      default:
        break;
    }
  }

  return (
    <main>
      <Navbar />
      <div className="flex min-h-screen flex-col items-center justify-between px-24 py-8 bg-gradient-to-r from-black to-blue-950">
        <h2 className="text-3xl font-bold text-gray-400 mb-8 flex items-start whitespace-pre">Select Attack <span className="text-sm text-red-500">*</span></h2>
        <AttackSelect attacks={attacks} onChange={(attack: string) => { setSelectedAttack(attack) }} />
        <HBar />
        <h2 className="text-3xl font-bold text-gray-400 mb-8 flex items-start whitespace-pre" id="model-select-header">Select Model <span className="text-sm text-red-500">*</span></h2>
        <ModelSelect models={attack === "TAG\n(Text Attack)" ? textModels : imageModels} onChange={(model: string) => { setSelectedModel(model) }} />
        <HBar />
        <h3 className="text-2xl font-bold text-gray-400 mb-8 flex items-start whitespace-pre" id="upload-pt-header">Upload Model Parameters <span className="text-sm text-red-500">*</span></h3>
        <div className="mb-4">
          <FileUpload
            expectedFileType="pt"
            label="Select File (.pt)"
            onFileChange={handlePtFileChange}
            nextElement={attack === "Inverting Gradients\n(Single Step)" ? "upload-zip-header" : "data-params-header"}
          />
          {ptFile && (
            <p className="mt-2 text-sm text-gray-400">{ptFile.name}</p>
          )}
        </div>
        <HBar />
        {attack === "Inverting Gradients\n(Single Step)" && <div>
          <h3 className="text-2xl text-center font-bold text-gray-400 mb-8 flex items-start whitespace-pre" id="upload-zip-header">Upload Custom Dataset <span className="text-sm text-red-500">*</span></h3>
          <div className="mb-4">
            <FileUpload
              expectedFileType="zip"
              label="Select File (.zip)"
              onFileChange={handleZipFileChange}
              nextElement="data-params-header"
            />
            {zipFile && (
              <p className="mt-2 text-sm text-gray-400">{zipFile.name}</p>
            )}
          </div>
          <HBar />
        </div>}
        <h3 className="text-2xl font-bold text-gray-400 mb-8" id="data-params-header">Dataset Parameters</h3>
        <DatasetParams
          datasetStructure={datasetStructure}
          handleStructureChange={handleStructureChange}
          handleDataParamsChange={handleDataParamsChange}
          attack={attack}
        />
        <HBar />
        <h3 className="text-2xl font-bold text-gray-400 mb-8">Attack Parameters</h3>
        <AttackParams handleAttackParamsChange={handleAttackParamsChange} />
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
