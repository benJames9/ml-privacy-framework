"use client";
import { useState } from "react";
import DatasetParams from "@/components/DatasetParams";
import FileUpload from "@/components/FileUpload";
import HBar from "@/components/HBar";
import ModelSelect from "@/components/ModelSelect";
import Navbar from "@/components/Navbar";
import AttackParams from "@/components/AttackParams";
import LoggingParams from "@/components/LoggingParams";
import EvaluateButton from "@/components/EvaluateButton";

export default function Home() {
  const models: string[] = ["ResNet-18", "Model 2", "Model 3", "Model 4"];
  const [model, setSelectedModel] = useState<string>(models[0]);
  const [ptFile, setSelectedPtFile] = useState<File | null>(null);
  const [zipFile, setSelectedZipFile] = useState<File | null>(null);

  // Dataset parameters
  const [datasetStructure, setDatasetStructure] = useState<"Foldered" | "CSV">("Foldered");
  const [csvPath, setCsvPath] = useState<string>("");
  const [datasetSize, setDatasetSize] = useState<number>(0);
  const [numClasses, setNumClasses] = useState<number>(0);
  const [batchSize, setBatchSize] = useState<number>(0);

  // Attack parameters
  const [numRestarts, setNumRestarts] = useState<number>(0);
  const [stepSize, setStepSize] = useState<number>(0);
  const [maxIterations, setMaxIterations] = useState<number>(0);

  // Logging parameters
  const [callbackInterval, setCallbackInterval] = useState<number>(0);

  const onClick = async () => {
    const formData = new FormData();

    // Append files to formData
    if (ptFile) formData.append("ptFile", ptFile);
    if (zipFile) formData.append("zipFile", zipFile);

    // Append text fields to formData
    formData.append("model", model);
    formData.append("datasetStructure", datasetStructure);
    formData.append("csvPath", csvPath);
    formData.append("datasetSize", datasetSize.toString());
    formData.append("numClasses", numClasses.toString());
    formData.append("batchSize", batchSize.toString());
    formData.append("numRestarts", numRestarts.toString());
    formData.append("stepSize", stepSize.toString());
    formData.append("maxIterations", maxIterations.toString());
    formData.append("callbackInterval", callbackInterval.toString());

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
    // TODO: add validation
    switch (field) {
      case "csvPath":
        setCsvPath(value);
        break;
      case "datasetSize":
        setDatasetSize(parseInt(value));
        break;
      case "numClasses":
        setNumClasses(parseInt(value));
        break;
      case "batchSize":
        setBatchSize(parseInt(value));
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
        setStepSize(parseInt(value));
        break;
      case "maxIterations":
        setMaxIterations(parseInt(value));
        break;
      default:
        break;
    }
  }

  const handleLoggingParamsChange = (value: string) => {
    setCallbackInterval(parseInt(value));
  }

  return (
    <main>
      <Navbar />
      <div className="flex min-h-screen flex-col items-center justify-between px-24 py-8 bg-gradient-to-r from-black to-blue-950">
        <h2 className="text-3xl font-bold text-gray-400 mb-8">Select Model</h2>
        <ModelSelect models={models} onChange={(model: string) => { setSelectedModel(model) }} />
        <HBar />
        <h3 className="text-2xl font-bold text-gray-400 mb-8" id="upload-pt-header">Upload Model Parameters</h3>
        <div className="mb-4">
          <FileUpload
            expectedFileType="pt"
            label="Select File (.pt)"
            onFileChange={handlePtFileChange}
            nextElement="upload-zip-header"
          />
          {ptFile && (
            <p className="mt-2 text-sm text-gray-400">{ptFile.name}</p>
          )}
        </div>
        <HBar />
        <h3 className="text-2xl font-bold text-gray-400 mb-8" id="upload-zip-header">Upload Custom Dataset</h3>
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
        <h3 className="text-2xl font-bold text-gray-400 mb-8" id="data-params-header">Dataset Parameters</h3>
        <DatasetParams
          datasetStructure={datasetStructure}
          handleStructureChange={handleStructureChange}
          handleDataParamsChange={handleDataParamsChange}
        />
        <HBar />
        <h3 className="text-2xl font-bold text-gray-400 mb-8">Attack Parameters</h3>
        <AttackParams handleAttackParamsChange={handleAttackParamsChange} />
        <HBar />
        <h3 className="text-2xl font-bold text-gray-400 mb-4">Logging Parameters</h3>
        <LoggingParams handleLoggingParamsChange={handleLoggingParamsChange} />
        <EvaluateButton onClick={onClick} />
      </div>
    </main>
  )
}
