import FileUpload from "./FileUpload"
import HBar from "./HBar"
import InfoPopup from "./InfoPopup"
import NumberInput from "./NumberInput"
import TextInput from "./TextInput"

interface MiaParamsProps {
  handleMiaParamsChange: (field: string, value: string | (File | null)) => void;
}

const MiaParams: React.FC<MiaParamsProps> = ({ handleMiaParamsChange }) => {
  return (
    <div>
      {/* Upload label dictionary */}
      <div className="flex items-start">
        <h3 className="text-2xl text-center font-bold text-gray-400 mb-8 flex items-start whitespace-pre" id="upload-label-dict-header">
          Upload Label Dictionary <span className="text-sm text-red-500">*</span>
        </h3>
        <InfoPopup text={"Upload a .json file containing the label dictionary to be used in the attack."} />
      </div>
      <div className="mb-4">
        <FileUpload
          expectedFileType="csv"
          label="Select File (.csv)"
          onFileChange={(file: File | null) => { handleMiaParamsChange("labelDict", file) }}
          nextElement="upload-target-image-header"
        />
      </div>
      <HBar />

      {/* Upload target image */}
      <div>
        <div className="flex items-start">
          <h3 className="text-2xl text-center font-bold text-gray-400 mb-8 flex items-start whitespace-pre" id="upload-target-image-header">
            Upload Target Image <span className="text-sm text-red-500">*</span>
          </h3>
          <InfoPopup text={"Upload a .zip file containing the target point to be used in the attack.\n\nIt should be organised as follows:\n\n dataset\n ├── class1\n │   ├── img1.jpg\n │   ├── img2.jpg\n │   └── ...\n └── class2\n     ├── img1.jpg\n     ├── img2.jpg\n     └── ..."} />
        </div>
        <FileUpload
          expectedFileType="JPEG"
          label="Select File (.JPEG)"
          onFileChange={(file: File | null) => { handleMiaParamsChange("targetImage", file) }}
        />
        <TextInput
          label="Target Label"
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => { handleMiaParamsChange("targetLabel", e.target.value) }}
          isRequired={true}
        />
      </div>
      <HBar />

      {/* Shadow Parameters */}
      <div className="flex items-start">
        <h3 className="text-2xl font-bold text-gray-400 mb-4">
          Shadow Parameters
        </h3>
        <InfoPopup text={"Enter the parameters of the shadow model to be used in the attack."} />
      </div>
      <NumberInput
        label="No. Shadow Models"
        onChange={(e: React.ChangeEvent<HTMLInputElement>) => { handleMiaParamsChange("numShadowModels", e.target.value) }}
        isRequired={true}
      />
      <NumberInput
        label="No. Data Points"
        onChange={(e: React.ChangeEvent<HTMLInputElement>) => { handleMiaParamsChange("numDataPoints", e.target.value) }}
        isRequired={true}
      />
      <NumberInput
        label="No. Epochs"
        onChange={(e: React.ChangeEvent<HTMLInputElement>) => { handleMiaParamsChange("numEpochs", e.target.value) }}
        isRequired={true}
      />
      <NumberInput
        label="Batch Size"
        onChange={(e: React.ChangeEvent<HTMLInputElement>) => { handleMiaParamsChange("shadowBatchSize", e.target.value) }}
        isRequired={true}
      />
      <NumberInput
        label="Learning Rate"
        onChange={(e: React.ChangeEvent<HTMLInputElement>) => { handleMiaParamsChange("learningRate", e.target.value) }}
        isRequired={true}
      />

    </div>
  );
};

export default MiaParams;