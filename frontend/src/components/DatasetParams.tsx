"use client";
import { useState } from "react";
import Radio from "./Radio";
import TextInput from "./TextInput";

const DatasetParams: React.FC = () => {
  const [datasetStructure, setDatasetStructure] = useState<"Foldered" | "CSV">("Foldered");
  const [csvPath, setCsvPath] = useState<string>("");

  const handleStructureChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    console.log(e.target.value);
    setDatasetStructure(e.target.value as "Foldered" | "CSV");
  }

  const handleInputChange = (field: string, value: string) => {
    switch (field) {
      case "csvPath":
        console.log(value);
        setCsvPath(value);
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
        <TextInput label="Path to CSV file:" onChange={(e) => handleInputChange("csvPath", e.target.value)} />
      )}
    </div>
  );
}

export default DatasetParams;
