"use client";
import TextInput from "./TextInput";
import NumberInput from "./NumberInput";
import ThreeNumberInput from "./ThreeNumberInput";
import SelectInput from "./SelectInput";

interface DatasetParamsProps {
  handleDataParamsChange: (field: string, value: string) => void;
  attack: string;
  textDatasets: string[];
  tokenizers: string[];
}

const DatasetParams: React.FC<DatasetParamsProps> = ({ handleDataParamsChange, attack, textDatasets, tokenizers }) => {
  return (
    <div>
      {attack === "invertinggradients" && <div>
        <ThreeNumberInput
          label="Image shape"
          onChange1={(e) => { handleDataParamsChange("imageShape1", e.target.value) }}
          onChange2={(e) => { handleDataParamsChange("imageShape2", e.target.value) }}
          onChange3={(e) => { handleDataParamsChange("imageShape3", e.target.value) }}
        />
        <ThreeNumberInput
          label="Mean"
          onChange1={(e) => { handleDataParamsChange("mean1", e.target.value) }}
          onChange2={(e) => { handleDataParamsChange("mean2", e.target.value) }}
          onChange3={(e) => { handleDataParamsChange("mean3", e.target.value) }}
        />
        <ThreeNumberInput
          label="Standard deviation"
          onChange1={(e) => { handleDataParamsChange("std1", e.target.value) }}
          onChange2={(e) => { handleDataParamsChange("std2", e.target.value) }}
          onChange3={(e) => { handleDataParamsChange("std3", e.target.value) }}
        />
      </div>}
      {attack === "tag" && <div>
        <SelectInput
          label="Text Dataset"
          options={textDatasets}
          onChange={(e) => handleDataParamsChange("textDataset", e.target.value)}
          isRequired={true}
        />
        <SelectInput
          label="Tokenizer"
          options={tokenizers}
          onChange={(e) => handleDataParamsChange("tokenizer", e.target.value)}
          isRequired={true}
        />
        <NumberInput
          label="No. data points"
          onChange={(e) => handleDataParamsChange("textDataPoints", e.target.value)}
          isRequired={true}
        />
        <NumberInput
          label="Sequence length"
          onChange={(e) => handleDataParamsChange("seqLength", e.target.value)}
          isRequired={true}
        />
      </div>}
      {attack !== "tag" && <NumberInput
        label="Batch size"
        onChange={(e) => handleDataParamsChange("batchSize", e.target.value)}
        isRequired={true}
      />
      }
    </div>
  );
}

export default DatasetParams;
