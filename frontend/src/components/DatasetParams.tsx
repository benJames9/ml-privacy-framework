"use client";
import { useState } from "react";
import Radio from "./Radio";

const DatasetParams: React.FC = () => {
  const [datasetStructure, setDatasetStructure] = useState<"Foldered" | "CSV">("Foldered");

  const handleStructureChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    console.log(e.target.value);
    setDatasetStructure(e.target.value as "Foldered" | "CSV");
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
    </div>
  );
}

export default DatasetParams;
