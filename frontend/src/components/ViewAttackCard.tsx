import { useState } from "react";

const ViewAttackCard: React.FC = () => {
  const [token, setToken] = useState<string>("");
  const onClick = () => {
    if (token !== "") {
      window.location.href = `/results/${token}`;
    }
  }
  return (
    <div className="bg-gradient-to-r from-blue-950 to-teal-900 border border-gray-700 rounded-lg p-8 md:p-12 scale-90">
      <h1 className="text-3xl text-gray-100 font-bold mb-8 text-center">View Previous Attack</h1>
      <p className="text-lg font-normal text-gray-300 mb-4">Want to view a previous attack? Just enter its token down below!</p>
      <p className="text-lg font-normal text-gray-300 mb-6">If the attack is still ongoing, you&rsquo;ll be able to watch its progress live, otherwise you&rsquo;ll see the final results.</p>

      <div className="relative text-center">
        <input
          type="text"
          value={token}
          onChange={(e) => setToken(e.target.value)}
          className="block w-full p-4 text-md border rounded-lg bg-gray-900 border-gray-700 placeholder-gray-300 text-white focus:ring-blue-500 focus:border-blue-500"
          placeholder="Enter token"
        />
        <button
          className="text-white absolute end-2.5 bottom-2.5 focus:ring-4 focus:outline-none font-medium rounded-lg text-sm px-4 py-2 bg-gradient-to-br from-teal-700 to-blue-700 hover:bg-gradient-to-bl focus:ring-blue-800"
          onClick={onClick}>
          View Attack
        </button>
      </div>
    </div>
  );
};

export default ViewAttackCard;