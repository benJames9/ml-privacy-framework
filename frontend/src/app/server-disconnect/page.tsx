"use client";

import { useSearchParams } from 'next/navigation'

const onClick = async () => {
  window.location.href = `/`;
}

const ConnectionClosedPage = () => {
  const searchParams = useSearchParams()
  const error = searchParams.get('error')

  return (
    <div className="min-h-screen flex flex-col justify-center items-center">
      <h1 className="text-3xl font-bold text-white-600 mb-4">
        {error}
      </h1>
      <div className="flex justify-center">
        <button
          type="button"
          className={
            `bg-gray-900 text-white hover:bg-gray-600 border border-gray-300 text-gray-700 font-medium rounded-lg text-center inline-flex items-center px-3 py-2 text-base`
          }
          onClick={onClick}
        >
          Return to Home Page
        </button>
      </div>
    </div>
  );
};
  
export default ConnectionClosedPage;