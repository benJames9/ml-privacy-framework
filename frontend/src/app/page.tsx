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
  const [selectedModel, setSelectedModel] = useState<string>("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

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

  const onClick = () => {
    console.log("Clicked");
    console.log("model", selectedModel);
    console.log("file:", selectedFile);
    console.log("structure:", datasetStructure);
    console.log("csvPath:", csvPath);
    console.log("datasetSize:", datasetSize);
    console.log("numClasses:", numClasses);
    console.log("batchSize:", batchSize);
    console.log("numRestarts:", numRestarts);
    console.log("stepSize:", stepSize);
    console.log("maxIterations:", maxIterations);
  }

  const handleFileChange = (file: File | null) => {
    setSelectedFile(file);
  }

  const handleStructureChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    console.log(e.target.value);
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

  return (
    <main>
      <Navbar />
      <div className="flex min-h-screen flex-col items-center justify-between px-24 py-8 bg-gradient-to-r from-black to-blue-950">
        <h2 className="text-3xl font-bold text-gray-400 mb-8">Select Model</h2>
        <ModelSelect models={models} onChange={(model: string) => { setSelectedModel(model) }} />
        <HBar />
        <h3 className="text-2xl font-bold text-gray-400 mb-8">Upload Model Parameters</h3>
        <div className="mb-4">
          <FileUpload
            expectedFileType="pt"
            label="Select File (.pt)"
            onFileChange={handleFileChange}
          />
          {selectedFile && (
            <p className="mt-2 text-sm text-gray-400">{selectedFile.name}</p>
          )}
        </div>
        <HBar />
        <h3 className="text-2xl font-bold text-gray-400 mb-8">Dataset Parameters</h3>
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
        <LoggingParams />
        <EvaluateButton onClick={onClick} />
      </div>
    </main>
  )
}
