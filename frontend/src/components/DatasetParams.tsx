"use client";
import Radio from "./Radio";
import TextInput from "./TextInput";
import NumberInput from "./NumberInput";
import ThreeNumberInput from "./ThreeNumberInput";
import SelectInput from "./SelectInput";

interface DatasetParamsProps {
  datasetStructure: "Foldered" | "CSV";
  handleDataParamsChange: (field: string, value: string) => void;
  handleStructureChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  attack: string;
}

const DatasetParams: React.FC<DatasetParamsProps> = ({ datasetStructure, handleDataParamsChange, handleStructureChange, attack }) => {
  return (
    <div>
      {attack === "Inverting Gradients\n(Single Step)" && <div>
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
        <ThreeNumberInput
          label="Image shape:"
          onChange1={(e) => { handleDataParamsChange("imageShape1", e.target.value) }}
          onChange2={(e) => { handleDataParamsChange("imageShape2", e.target.value) }}
          onChange3={(e) => { handleDataParamsChange("imageShape3", e.target.value) }}
        />
        <ThreeNumberInput
          label="Mean:"
          onChange1={(e) => { handleDataParamsChange("mean1", e.target.value) }}
          onChange2={(e) => { handleDataParamsChange("mean2", e.target.value) }}
          onChange3={(e) => { handleDataParamsChange("mean3", e.target.value) }}
        />
        <ThreeNumberInput
          label="Standard deviation:"
          onChange1={(e) => { handleDataParamsChange("std1", e.target.value) }}
          onChange2={(e) => { handleDataParamsChange("std2", e.target.value) }}
          onChange3={(e) => { handleDataParamsChange("std3", e.target.value) }}
        />
      </div>}
      {attack === "TAG\n(Text Attack)" && <div>
        <SelectInput
          label="Text Dataset:"
          options={["CoLA", "Random Tokens", "Stack Overflow", "WikiText"]}
          onChange={(e) => handleDataParamsChange("textDataset", e.target.value)}
        />
        <NumberInput
          label="No. data points:"
          onChange={(e) => handleDataParamsChange("numDataPoints", e.target.value)}
        />
        <NumberInput
          label="Sequence length:"
          onChange={(e) => handleDataParamsChange("seqLength", e.target.value)}
        />
      </div>}
      <NumberInput
        label="Batch size:"
        onChange={(e) => handleDataParamsChange("batchSize", e.target.value)}
      />
    </div>
  );
}

export default DatasetParams;
