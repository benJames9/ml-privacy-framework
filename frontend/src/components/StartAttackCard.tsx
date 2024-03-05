const StartAttackCard: React.FC = () => {
  return (
    <div className="bg-gradient-to-r from-blue-950 to-purple-950 border border-gray-700 rounded-lg p-8 md:p-12">
      <h1 className="text-3xl text-gray-100 font-bold mb-8 text-center">Start New Attack</h1>
      <p className="text-lg font-normal text-gray-300 mb-4">
        Choose between a variety of <strong>image</strong> and <strong>text</strong> attacks to execute on a model of your choice.
      </p>
      <p className="text-lg font-normal text-gray-300 mb-6">
        You can either use one of our pre-trained models or upload your own model to execute the attack on.
      </p>
      <div className="text-center">
        <button
          type="button"
          className="relative inline-flex mx-auto items-center justify-center p-0.5 me-2 overflow-hidden text-md font-medium rounded-lg group bg-gradient-to-br from-purple-600 to-blue-500 group-hover:from-purple-600 group-hover:to-blue-500 hover:text-white text-white focus:ring-4 focus:outline-none focus:ring-blue-800"
          onClick={() => window.location.href = "/setup"}
        >
          <span className="relative px-5 py-2.5 transition-all ease-in duration-75 bg-gray-900 rounded-md group-hover:bg-opacity-0 flex items-center">  Set up Attack
            <svg className="w-3.5 h-3.5 ml-2 rtl:rotate-180" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 14 10">
              <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M1 5h12m0 0L9 1m4 4L9 9" />
            </svg>
          </span>
        </button>
      </div>
    </div>
  );
}

export default StartAttackCard;