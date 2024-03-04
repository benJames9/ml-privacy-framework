interface SaveTokenButtonProps {
  token: number;
}

const SaveTokenButton: React.FC<SaveTokenButtonProps> = ({ token }) => {
  return (
    <div>
      <button
        onClick={() => {
          navigator.clipboard.writeText(token.toString());
        }}
        className="text-white bg-gradient-to-br from-blue-500 to-green-800 hover:bg-gradient-to-bl focus:ring-4 focus:outline-none focus:ring-blue-800 font-bold rounded-lg text-2xl px-8 py-4 text-center mx-4">
        Save Token
      </button>
    </div>
  );
}

export default SaveTokenButton;