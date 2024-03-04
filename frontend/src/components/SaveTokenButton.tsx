interface SaveTokenButtonProps {
  onClick: () => void;
}

const SaveTokenButton: React.FC<SaveTokenButtonProps> = ({ onClick }) => {
  return (
    <div>
      <button
        onClick={onClick}
        className="text-white bg-gradient-to-br from-blue-500 to-purple-800 hover:bg-gradient-to-bl focus:ring-4 focus:outline-none focus:ring-blue-800 font-bold rounded-lg text-2xl px-8 py-4 text-center mx-4">
        Copy Token
      </button>
    </div>
  );
}

export default SaveTokenButton;