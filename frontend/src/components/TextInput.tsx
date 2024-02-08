interface TextInputProps {
  label: string;
}

const TextInput: React.FC<TextInputProps> = ({ label }) => {
  return (
    <div className="flex mt-4 justify-between items-center">
      <h3 className="font-semibold text-white mr-4">{label}</h3>
      <input type="text" className="bg-gray-100 border border-gray-300 rounded-md py-2 px-3 focus:ring-blue-500 focus:border-blue-500 sm:text-sm" />
    </div>
  )
}

export default TextInput;