interface EvaluateButtonProps {
  onClick: () => void;
}

const EvaluateButton: React.FC<EvaluateButtonProps> = ({ onClick }) => {
  return (
    <button
      type="button"
      className="text-white bg-gradient-to-br from-purple-600 to-blue-500 hover:bg-gradient-to-bl focus:ring-4 focus:outline-none focus:ring-blue-800 font-bold rounded-lg text-2xl px-8 py-4 text-center my-10"
      onClick={onClick}
    >
      Evaluate
    </button>
  )
}

export default EvaluateButton;