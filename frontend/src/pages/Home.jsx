import React from 'react';
import { Link } from 'react-router-dom';
import { FiCompass, FiCpu, FiAward } from 'react-icons/fi';

export default function Home() {
  return (
    <div className="max-w-4xl mx-auto px-6 py-12 space-y-12">
      <div className="text-center space-y-4">
        <div className="w-16 h-16 bg-blue-50 rounded-2xl flex items-center justify-center text-blue-600 mx-auto">
          <FiAward className="w-8 h-8" />
        </div>
        <h1 className="text-3xl md:text-4xl font-extrabold text-gray-800 tracking-tight">
          AI-Powered Government Scheme Discovery
        </h1>
        <p className="text-xs md:text-sm text-gray-500 max-w-xl mx-auto leading-relaxed">
          Navigate through complex criteria with our Agentic AI assistant, which simplifies documentation checks and verifies your eligibility in real time.
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-6 pt-4">
        <Link 
          to="/chat" 
          className="p-6 bg-white hover:bg-blue-50/10 border border-gray-100 hover:border-blue-300 rounded-3xl transition shadow-sm hover:shadow-md space-y-3 cursor-pointer group"
        >
          <div className="w-10 h-10 bg-blue-50 text-blue-600 rounded-xl flex items-center justify-center group-hover:bg-blue-600 group-hover:text-white transition">
            <FiCpu className="w-5 h-5" />
          </div>
          <h2 className="text-base font-bold text-gray-800">Converse with AI</h2>
          <p className="text-xs text-gray-500 leading-relaxed">
            Talk to our AI Agent in plain English (or native languages) to dynamically discover schemes matching your specific life scenario.
          </p>
        </Link>

        <Link 
          to="/explorer" 
          className="p-6 bg-white hover:bg-green-50/10 border border-gray-100 hover:border-green-300 rounded-3xl transition shadow-sm hover:shadow-md space-y-3 cursor-pointer group"
        >
          <div className="w-10 h-10 bg-green-50 text-green-600 rounded-xl flex items-center justify-center group-hover:bg-green-600 group-hover:text-white transition">
            <FiCompass className="w-5 h-5" />
          </div>
          <h2 className="text-base font-bold text-gray-800">Browse Schemes Directory</h2>
          <p className="text-xs text-gray-500 leading-relaxed">
            Explore categories, apply state filters, and inspect eligibility details of central and state government offerings.
          </p>
        </Link>
      </div>
    </div>
  );
}
