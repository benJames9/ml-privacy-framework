interface SelectInputProps {
  label: string;
  options: string[];
  onChange: (event: React.ChangeEvent<HTMLSelectElement>) => void;
  isRequired?: boolean;
}

const SelectInput: React.FC<SelectInputProps> = ({ label, options, onChange, isRequired = false }) => {
  return (
    <div className="flex mt-4 justify-between items-center">
      <h3 className="font-semibold text-white mr-4 flex items-start whitespace-pre">{label} {isRequired && <span className="text-sm text-red-500">*</span>}</h3>
      <select
        onChange={onChange}
        className="min-w-[212px] text-black font-semibold bg-gray-300 border border-gray-500 rounded-md py-2 px-3 focus:ring-blue-500 focus:border-blue-500 sm:text-sm "
      >
        {options.map((option, index) => (
          <option key={index} value={option}>
            {option}
          </option>
        ))}
      </select>
    </div>
  );
};

export default SelectInput;
