"use client";
import { useState } from "react";
import Radio from "./Radio";
import TextInput from "./TextInput";
import NumberInput from "./NumberInput";

const DatasetParams: React.FC = () => {
  const [datasetStructure, setDatasetStructure] = useState<"Foldered" | "CSV">("Foldered");
  const [csvPath, setCsvPath] = useState<string>("");
  const [datasetSize, setDatasetSize] = useState<number>(0);
  const [numClasses, setNumClasses] = useState<number>(0);
  const [batchSize, setBatchSize] = useState<number>(0);

  const handleStructureChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    console.log(e.target.value);
    setDatasetStructure(e.target.value as "Foldered" | "CSV");
  }

  const handleInputChange = (field: string, value: string) => {
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

  return (
    <div>
      <div className="flex items-center">
        <h3 className="font-semibold text-white mr-4">Structure of Dataset:</h3>
        <div className="flex items-center space-x-3">
          <Radio value="Foldered" checked={datasetStructure === "Foldered"} onChange={handleStructureChange} />
          <Radio value="CSV" checked={datasetStructure === "CSV"} onChange={handleStructureChange} />
        </div>
      </div>
      {datasetStructure === "CSV" && (
        <TextInput
          label="Path to CSV file:"
          onChange={(e) => handleInputChange("csvPath", e.target.value)}
        />
      )}
      <NumberInput
        label="Size of dataset:"
        onChange={(e) => handleInputChange("datasetSize", e.target.value)}
      />
      <NumberInput
        label="Number of classes:"
        onChange={(e) => handleInputChange("numClasses", e.target.value)}
      />
      <NumberInput
        label="Batch Size:"
        onChange={(e) => handleInputChange("batchSize", e.target.value)}
      />
    </div>
  );
}

export default DatasetParams;
