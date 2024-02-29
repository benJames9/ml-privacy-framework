import { useRef } from "react";

interface NumberInputProps {
  label: string;
  onChange: (event: React.ChangeEvent<HTMLInputElement>) => void;
}

const NumberInput: React.FC<NumberInputProps> = ({ label, onChange }) => {
  const inputRef = useRef<HTMLInputElement>(null);
  const handleWheel = (e: React.WheelEvent<HTMLInputElement>) => {
    e.preventDefault();
    inputRef.current!.blur();
    setTimeout(() => {
      inputRef.current!.focus();
    }, 0)
  }

  return (
    <div className="flex mt-4 justify-between items-center">
      <h3 className="font-semibold text-white mr-4">{label}</h3>
      <input
        type="number"
        onChange={onChange}
        ref={inputRef}
        onWheel={handleWheel}
        className="text-black bg-gray-300 border border-gray-500 rounded-md py-2 px-3 focus:ring-blue-500 focus:border-blue-500 sm:text-sm" />
    </div>
  )
}

export default NumberInput;
