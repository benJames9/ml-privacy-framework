interface CancelButtonProps {
    onClick: () => void;
  }

  const CancelButton: React.FC<CancelButtonProps> = ({ onClick }) => {
    return (
      <button
        type="button"
        className="text-white bg-gradient-to-br from-red-600 to-blue-900 hover:bg-gradient-to-bl focus:ring-4 focus:outline-none focus:ring-blue-800 font-bold rounded-lg text-2xl px-8 py-4 text-center mx-4"
        onClick={onClick}
      >
        Cancel
      </button>
    )
  }

  export default CancelButton;
