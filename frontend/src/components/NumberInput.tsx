interface NumberInputProps {
  label: string;
  onChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  isRequired?: boolean;
}

const NumberInput: React.FC<NumberInputProps> = ({ label, onChange, isRequired = false }) => {
  return (
    <div className="flex mt-4 justify-between items-center">
      <h3 className="font-semibold mr-4 text-white flex items-start whitespace-pre">{label} {isRequired && <span className="text-sm text-red-500">*</span>}</h3>
      <input
        type="number"
        min="0"
        onChange={onChange}
        onWheel={e => { e.currentTarget.blur() }}
        className="text-black w-[202px] bg-gray-300 border border-gray-500 rounded-md py-2 px-3 focus:ring-blue-500 focus:border-blue-500 sm:text-sm" />
    </div>
  )
}

export default NumberInput;
