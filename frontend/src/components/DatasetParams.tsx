"use client";
import { useState } from "react";
import Radio from "./Radio";
import TextInput from "./TextInput";
import NumberInput from "./NumberInput";

interface DatasetParamsProps {
  datasetStructure: "Foldered" | "CSV";
  handleDataParamsChange: (field: string, value: string) => void;
  handleStructureChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
}

const DatasetParams: React.FC<DatasetParamsProps> = ({ datasetStructure, handleDataParamsChange, handleStructureChange }) => {
  return (
    <div>
      <div className="flex items-center">
        <h3 className="font-semibold text-white mr-4">Structure of dataset:</h3>
        <div className="flex items-center space-x-3">
          <Radio value="Foldered" checked={datasetStructure === "Foldered"} onChange={handleStructureChange} />
          <Radio value="CSV" checked={datasetStructure === "CSV"} onChange={handleStructureChange} />
        </div>
      </div>
      {datasetStructure === "CSV" && (
        <TextInput
          label="Path to CSV file:"
          onChange={(e) => handleDataParamsChange("csvPath", e.target.value)}
        />
      )}
      <NumberInput
        label="Size of dataset:"
        onChange={(e) => handleDataParamsChange("datasetSize", e.target.value)}
      />
      <NumberInput
        label="Number of classes:"
        onChange={(e) => handleDataParamsChange("numClasses", e.target.value)}
      />
      <NumberInput
        label="Batch size:"
        onChange={(e) => handleDataParamsChange("batchSize", e.target.value)}
      />
    </div>
  );
}

export default DatasetParams;
