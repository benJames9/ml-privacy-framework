interface ThreeNumberInputProps {
  label: string;
  onChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
}

const ThreeNumberInput: React.FC<ThreeNumberInputProps> = ({ label, onChange }) => {
  return (
    <div className="flex mt-4 justify-between items-center">
      <h3 className="font-semibold text-white mr-4">{label}</h3>
      <div className="justify-between">
        <input
          type="number"
          min="0"
          onChange={onChange}
          className="text-black w-[65px] bg-gray-300 border border-gray-500 rounded-md py-2 px-3 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
        />
        <input
          type="number"
          min="0"
          onChange={onChange}
          className="text-black w-[65px] ml-2 bg-gray-300 border border-gray-500 rounded-md py-2 px-3 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
        />
        <input
          type="number"
          min="0"
          onChange={onChange}
          className="text-black w-[65px] ml-2 bg-gray-300 border border-gray-500 rounded-md py-2 px-3 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
        />
      </div>
    </div>
  );
}

export default ThreeNumberInput;