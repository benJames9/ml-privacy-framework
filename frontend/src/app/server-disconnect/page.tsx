"use client";

import { useSearchParams } from 'next/navigation'
import Navbar from "@/components/Navbar";

const onClick = async () => {
  window.location.href = `/`;
}

const ConnectionClosedPage = () => {
  const searchParams = useSearchParams()
  const error = searchParams.get('error')

  return (
    <main>
      <Navbar />
      <div className="flex min-h-screen flex-col items-center text-center px-24 py-8 bg-gradient-to-r from-black to-blue-950">
        <h1 className="text-3xl font-bold text-white-600 mt-16 mb-8">
          {error || "Unknown Error"}
        </h1>
        <button
          type="button"
          className={
            `bg-gray-900 text-white hover:bg-gray-600 border border-gray-300 text-gray-700 font-medium rounded-lg text-center inline-flex items-center px-3 py-2 mt-4 text-base`
          }
          onClick={onClick}
        >
          Return to Home Page
        </button>
      </div>
    </main>
  );
};

export default ConnectionClosedPage;
