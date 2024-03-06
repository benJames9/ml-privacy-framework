import { useState } from "react";

interface InfoPopupProps {
  text: string;
}

const InfoPopup: React.FC<InfoPopupProps> = ({ text }) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="flex items-center">
      <button
        className="relative ml-4 bg-gray-800 hover:bg-gray-600 rounded-full p-2"
        aria-describedby="upload-pt-info"
        onMouseEnter={() => setIsOpen(true)}
        onMouseLeave={() => setIsOpen(false)}
      >
        <svg className="w-4 h-4 text-gray-400" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
          <circle cx="10" cy="4" r="2.4" />
          <path d="M8 8v10h4V8z" />
        </svg>
      </button>
      {isOpen && (
        <div
          className="absolute z-10 ml-14 bg-gray-800 rounded-md shadow-lg max-w-xs overflow-hidden"
          id="upload-pt-info"
        >
          <div className="w-full px-4 py-3 text-sm text-gray-400">
            {text}
          </div>
        </div>
      )}
    </div>
  );
}

export default InfoPopup;