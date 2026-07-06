import React from 'react';
import { FiX, FiFileText, FiAward, FiInfo, FiLayers, FiCalendar } from 'react-icons/fi';

export default function SchemeDetailDrawer({ scheme, onClose }) {
  if (!scheme) return null;

  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      {/* Backdrop overlay */}
      <div 
        onClick={onClose}
        className="fixed inset-0 bg-gray-950/40 backdrop-blur-xs transition-opacity animate-fade-in" 
      />

      {/* Slide-over panel container */}
      <div className="relative w-full max-w-md bg-white h-full shadow-2xl flex flex-col z-10 animate-slide-left border-l border-gray-150">
        
        {/* Panel Header */}
        <div className="p-5 border-b border-gray-100 flex items-center justify-between bg-gray-50/50">
          <div className="space-y-0.5 max-w-[85%]">
            <span className="text-[10px] text-blue-600 font-extrabold uppercase tracking-wider">
              {scheme.ministry || "Ministry of Welfare"}
            </span>
            <h2 className="text-base font-extrabold text-gray-800 leading-tight truncate">
              {scheme.title || scheme.name}
            </h2>
          </div>
          <button 
            type="button"
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-xl transition text-gray-400 hover:text-gray-600 cursor-pointer"
          >
            <FiX className="w-5 h-5" />
          </button>
        </div>

        {/* Content body */}
        <div className="flex-1 overflow-y-auto p-5 space-y-5 text-xs leading-relaxed text-gray-650">
          
          {/* Description */}
          <div className="space-y-1.5">
            <div className="flex items-center space-x-2 text-gray-800 font-bold">
              <FiInfo className="w-4 h-4 text-blue-500" />
              <span>Description</span>
            </div>
            <p className="text-gray-500 pl-6 leading-relaxed">{scheme.description}</p>
          </div>

          {/* Benefits */}
          <div className="space-y-1.5">
            <div className="flex items-center space-x-2 text-gray-800 font-bold">
              <FiAward className="w-4 h-4 text-green-600" />
              <span>Key Benefits</span>
            </div>
            <div className="pl-6">
              <p className="p-3 bg-green-50/20 border border-green-150/40 text-green-950 rounded-2xl font-semibold">
                {scheme.benefits || "Details of monetary/non-monetary benefits."}
              </p>
            </div>
          </div>

          {/* Eligibility Requirements */}
          <div className="space-y-1.5">
            <div className="flex items-center space-x-2 text-gray-800 font-bold">
              <FiLayers className="w-4 h-4 text-purple-600" />
              <span>Eligibility Requirements</span>
            </div>
            <div className="pl-6">
              <div className="p-3 bg-gray-50 border border-gray-100 rounded-2xl space-y-2 text-[11px]">
                <div className="flex justify-between border-b border-gray-100/50 pb-1.5">
                  <span className="text-gray-455 font-semibold">State</span>
                  <span className="font-extrabold text-gray-700 capitalize">{scheme.eligibility?.state || scheme.state || "Central"}</span>
                </div>
                <div className="flex justify-between border-b border-gray-100/50 pb-1.5">
                  <span className="text-gray-455 font-semibold">Gender</span>
                  <span className="font-extrabold text-gray-700">{scheme.eligibility?.gender || 'All'}</span>
                </div>
                {(scheme.eligibility?.minAge || scheme.eligibility?.maxAge) && (
                  <div className="flex justify-between border-b border-gray-100/50 pb-1.5">
                    <span className="text-gray-455 font-semibold">Age Bracket</span>
                    <span className="font-extrabold text-gray-700">
                      {scheme.eligibility.minAge || 0} - {scheme.eligibility.maxAge || 'No limit'} years
                    </span>
                  </div>
                )}
                {scheme.eligibility?.incomeLimit && (
                  <div className="flex justify-between">
                    <span className="text-gray-455 font-semibold">Max Income Limit</span>
                    <span className="font-extrabold text-gray-700">₹{scheme.eligibility.incomeLimit.toLocaleString()} / year</span>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Documents checklist */}
          {scheme.documentsRequired?.length > 0 && (
            <div className="space-y-1.5">
              <div className="flex items-center space-x-2 text-gray-800 font-bold">
                <FiFileText className="w-4 h-4 text-blue-500" />
                <span>Documents Needed</span>
              </div>
              <div className="pl-6">
                <ul className="space-y-1.5">
                  {scheme.documentsRequired.map((doc, idx) => (
                    <li key={idx} className="flex items-center space-x-2 text-[11px] font-semibold text-gray-750">
                      <div className="w-1.5 h-1.5 bg-blue-500 rounded-full flex-shrink-0" />
                      <span>{doc}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}

          {/* Deadline */}
          {scheme.deadline && (
            <div className="space-y-1.5">
              <div className="flex items-center space-x-2 text-gray-850 font-bold">
                <FiCalendar className="w-4 h-4 text-amber-500" />
                <span>Application Deadline</span>
              </div>
              <p className="text-amber-800 font-semibold pl-6">{scheme.deadline}</p>
            </div>
          )}
        </div>

        {/* Submit apply action */}
        {scheme.applicationUrl && (
          <div className="p-4 border-t border-gray-100 bg-gray-50/50 flex-shrink-0">
            <a
              href={scheme.applicationUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="block text-center w-full py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-bold transition shadow-sm cursor-pointer"
            >
              Apply Online
            </a>
          </div>
        )}
      </div>
    </div>
  );
}
