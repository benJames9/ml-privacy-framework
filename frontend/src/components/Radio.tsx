interface RadioProps {
  value: string;
  checked: boolean;
  onChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
}

const Radio: React.FC<RadioProps> = ({ value, checked, onChange }) => {
  return (
    <div className={`border ${checked ? "border-blue-500" : "border-gray-600"} rounded-lg px-4 py-3`}>
      <label htmlFor={`radio-{value}`} className="flex items-center">
        <input
          type="radio"
          id={`radio-{value}`}
          name="dataset-structure"
          value={value}
          checked={checked}
          className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300"
          onChange={onChange}
        />
        <span className="ml-2 font-medium text-sm text-gray-300">{value}</span>
      </label>
    </div>
  );
}

export default Radio;
