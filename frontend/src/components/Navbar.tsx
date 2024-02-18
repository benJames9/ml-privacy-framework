import React from 'react';

const Navbar: React.FC = () => {
  return (
    <nav className="bg-gray-800 text-white font-bold w-full z-50 p-6">
      <a href="/">
        <div className="container mx-auto flex">
          <div className="grid grid-cols-1 items-center justify-center w-full">
            <h1 className="text-5xl font-display lg:text-5xl mx-auto">Model<span className="italic text-blue-600">SAFE</span></h1>
            <h2 className="text-1xl italic font-medium lg:text-1xl mx-auto mt-2">Secure Adversarial Federated Evaluation</h2>
          </div>
        </div>
      </a>
    </nav>
  );
};

export default Navbar;
