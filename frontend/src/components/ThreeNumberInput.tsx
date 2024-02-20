interface ThreeNumberInputProps {
  label: string;
  onChange1: (event: React.ChangeEvent<HTMLInputElement>) => void;
  onChange2: (event: React.ChangeEvent<HTMLInputElement>) => void;
  onChange3: (event: React.ChangeEvent<HTMLInputElement>) => void;
}

const ThreeNumberInput: React.FC<ThreeNumberInputProps> = ({ label, onChange1, onChange2, onChange3 }) => {
  return (
    <div className="flex mt-4 justify-between items-center">
      <h3 className="font-semibold text-white mr-4">{label}</h3>
      <div className="justify-between">
        <input
          type="number"
          min="0"
          onChange={onChange1}
          className="text-black w-[65px] bg-gray-300 border border-gray-500 rounded-md py-2 px-3 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
        />
        <input
          type="number"
          min="0"
          onChange={onChange2}
          className="text-black w-[65px] ml-2 bg-gray-300 border border-gray-500 rounded-md py-2 px-3 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
        />
        <input
          type="number"
          min="0"
          onChange={onChange3}
          className="text-black w-[65px] ml-2 bg-gray-300 border border-gray-500 rounded-md py-2 px-3 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
        />
      </div>
    </div>
  );
}

export default ThreeNumberInput;