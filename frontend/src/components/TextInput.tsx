interface TextInputProps {
  label: string;
  onChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
}

const TextInput: React.FC<TextInputProps> = ({ label, onChange }) => {
  return (
    <div className="flex mt-4 justify-between items-center">
      <h3 className="font-semibold text-white mr-4">{label}</h3>
      <input
        type="text"
        onChange={onChange}
        className="text-black bg-gray-300 border border-gray-500 rounded-md py-2 px-3 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
      />
    </div>
  )
}

export default TextInput;
