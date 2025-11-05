import React from 'react';

const Header: React.FC = () => {
  return (
    <header className="bg-white shadow-md">
      <div className="container mx-auto px-4 lg:px-8 py-4 text-center">
        <h1 className="text-xl md:text-3xl font-bold text-gray-900 tracking-tight">
          <span className="block text-lg md:text-xl font-medium text-gray-600">Welcome to Daniel Signs</span>
          Day's Rental - Sticker Order Portal
        </h1>
      </div>
    </header>
  );
};

export default Header;