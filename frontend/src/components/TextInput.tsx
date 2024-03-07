interface TextInputProps {
  label: string;
  onChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
  isRequired?: boolean;
}

const TextInput: React.FC<TextInputProps> = ({ label, onChange, isRequired = false }) => {
  return (
    <div className="flex mt-4 items-center w-full">
      <h3 className="font-semibold text-white mr-5 flex items-start whitespace-pre">{label} {isRequired && <span className="text-sm text-red-500">*</span>}</h3>
      <input
        type="text"
        onChange={onChange}
        className="text-black bg-gray-300 border border-gray-500 rounded-md py-2 px-auto focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
      />
    </div>
  )
}

export default TextInput;
