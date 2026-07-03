import React from 'react';
import { Link } from 'react-router-dom';
import { FiAward } from 'react-icons/fi';

export default function Navbar() {
  return (
    <nav className="bg-white border-b border-gray-100 px-6 py-4 flex items-center justify-between shadow-sm sticky top-0 z-50">
      <Link to="/" className="flex items-center space-x-2.5">
        <div className="w-9 h-9 bg-blue-600 rounded-xl flex items-center justify-center text-white font-bold">
          <FiAward className="w-5 h-5" />
        </div>
        <div>
          <span className="font-extrabold text-base tracking-tight text-gray-800">UPLIFT</span>
          <span className="text-[9px] text-gray-400 font-bold block uppercase -mt-1 tracking-wider">AI RECOMMENDATIONS</span>
        </div>
      </Link>
      
      <div className="flex items-center space-x-4 text-xs font-semibold">
        <Link to="/chat" className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl transition shadow-sm">
          Launch Chat
        </Link>
      </div>
    </nav>
  );
}
