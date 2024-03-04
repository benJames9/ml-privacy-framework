interface NumberInputProps {
  label: string;
  onChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  isRequired?: boolean;
}

const NumberInput: React.FC<NumberInputProps> = ({ label, onChange, isRequired = false }) => {
  return (
    <div className="flex mt-4 justify-between items-center">
      <h3 className="font-semibold text-white mr-4 flex items-start whitespace-pre">{label} {isRequired && <span className="text-sm text-red-500">*</span>}</h3>
      <input
        type="number"
        onChange={onChange}
        onWheel={e => { e.currentTarget.blur() }}
        className="text-black bg-gray-300 border border-gray-500 rounded-md py-2 px-3 focus:ring-blue-500 focus:border-blue-500 sm:text-sm" />
    </div>
  )
}

export default NumberInput;
