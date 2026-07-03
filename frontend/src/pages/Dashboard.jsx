import React from 'react';
import { useChatStore } from '../store/useChatStore';
import { Link } from 'react-router-dom';
import { FiCheckSquare, FiAlertOctagon, FiStar, FiGrid } from 'react-icons/fi';

export default function Dashboard() {
  const { profileSummary, eligibleSchemes, missingInfo } = useChatStore();
  const profileKeys = Object.keys(profileSummary || {});

  return (
    <div className="max-w-5xl mx-auto px-6 py-8 space-y-6 animate-fade-in">
      <div>
        <h1 className="text-2xl font-black text-gray-800">User Dashboard</h1>
        <p className="text-xs text-gray-400 font-medium">Aggregated stats from your active AI recommendations session</p>
      </div>

      <div className="grid md:grid-cols-3 gap-5">
        
        {/* Attribute Count */}
        <div className="bg-white border border-gray-100 p-5 rounded-2xl shadow-sm flex items-center space-x-4">
          <div className="w-10 h-10 bg-blue-50 rounded-xl flex items-center justify-center text-blue-600">
            <FiCheckSquare className="w-5 h-5" />
          </div>
          <div>
            <span className="text-[10px] text-gray-400 font-bold uppercase tracking-wider block">Verified Attributes</span>
            <span className="text-lg font-extrabold text-gray-800">{profileKeys.length}</span>
          </div>
        </div>

        {/* Required Count */}
        <div className="bg-white border border-gray-100 p-5 rounded-2xl shadow-sm flex items-center space-x-4">
          <div className="w-10 h-10 bg-amber-50 rounded-xl flex items-center justify-center text-amber-600">
            <FiAlertOctagon className="w-5 h-5" />
          </div>
          <div>
            <span className="text-[10px] text-gray-400 font-bold uppercase tracking-wider block">Pending Attributes</span>
            <span className="text-lg font-extrabold text-gray-800">{missingInfo.length}</span>
          </div>
        </div>

        {/* Schemes Match Count */}
        <div className="bg-white border border-gray-100 p-5 rounded-2xl shadow-sm flex items-center space-x-4">
          <div className="w-10 h-10 bg-green-50 rounded-xl flex items-center justify-center text-green-600">
            <FiStar className="w-5 h-5" />
          </div>
          <div>
            <span className="text-[10px] text-gray-400 font-bold uppercase tracking-wider block">Eligible Schemes</span>
            <span className="text-lg font-extrabold text-gray-800">{eligibleSchemes.length}</span>
          </div>
        </div>

      </div>

      <div className="grid md:grid-cols-2 gap-6">
        
        {/* Profile Card details */}
        <div className="bg-white border border-gray-100 rounded-3xl p-5 shadow-sm space-y-4">
          <h2 className="text-sm font-bold text-gray-800 border-b border-gray-50 pb-2">Active Profile Parameters</h2>
          {profileKeys.length === 0 ? (
            <p className="text-xs text-gray-400 italic">No parameters collected. Chat with the AI assistant to begin.</p>
          ) : (
            <div className="grid grid-cols-2 gap-3">
              {profileKeys.map((key) => (
                <div key={key} className="p-3 bg-gray-50 border border-gray-100 rounded-xl text-xs space-y-1">
                  <span className="text-gray-400 font-bold uppercase tracking-wider text-[8px] block">
                    {key.replace('_', ' ')}
                  </span>
                  <span className="text-gray-750 font-extrabold block capitalize">
                    {String(profileSummary[key])}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Recommendations list matches */}
        <div className="bg-white border border-gray-100 rounded-3xl p-5 shadow-sm space-y-4">
          <h2 className="text-sm font-bold text-gray-800 border-b border-gray-50 pb-2">Verified Matches</h2>
          {eligibleSchemes.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-10 text-center space-y-2 border border-dashed border-gray-150 rounded-2xl">
              <FiGrid className="w-8 h-8 text-gray-300" />
              <p className="text-xs text-gray-400 italic">No schemes found yet.</p>
            </div>
          ) : (
            <div className="space-y-2.5 max-h-[250px] overflow-y-auto pr-0.5">
              {eligibleSchemes.map((scheme) => (
                <div 
                  key={scheme.id || scheme.scheme_id} 
                  className="p-3.5 bg-green-50/20 border border-green-150/40 rounded-2xl flex justify-between items-center"
                >
                  <div className="space-y-0.5">
                    <span className="font-bold text-xs text-gray-800 block">{scheme.title || scheme.name}</span>
                    <span className="text-[9px] text-gray-450 capitalize font-medium block">{scheme.category}</span>
                  </div>
                  <Link
                    to={`/explorer?id=${scheme.id || scheme.scheme_id}`}
                    className="text-[10px] font-bold text-blue-600 bg-white border border-gray-150 px-2.5 py-1 rounded-xl shadow-sm hover:border-blue-400 transition"
                  >
                    View Details
                  </Link>
                </div>
              ))}
            </div>
          )}
        </div>

      </div>
    </div>
  );
}
