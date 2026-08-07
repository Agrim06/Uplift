import React from 'react';
import { FiX, FiFileText, FiAward, FiInfo, FiLayers, FiCalendar, FiExternalLink } from 'react-icons/fi';

export default function SchemeDetailDrawer({ scheme, onClose }) {
  if (!scheme) return null;

  const applyUrl = scheme.application_link || scheme.applicationUrl || scheme.applicationLink || scheme.official_source;

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
              {scheme.ministry || scheme.scheme_type || "Government Scheme"}
            </span>
            <h2 className="text-base font-extrabold text-gray-800 leading-tight truncate">
              {scheme.title || scheme.name}
            </h2>
          </div>
          <button 
            type="button"
            onClick={onClose}
            className="w-8 h-8 rounded-full bg-gray-100 hover:bg-gray-200 text-gray-500 flex items-center justify-center transition cursor-pointer"
          >
            <FiX className="w-4 h-4" />
          </button>
        </div>

        {/* Scrollable details view */}
        <div className="flex-1 overflow-y-auto p-5 space-y-6 text-xs text-gray-700">
          
          {/* Objective Summary */}
          <div className="space-y-2">
            <div className="flex items-center space-x-2 text-gray-850 font-bold">
              <FiInfo className="w-4 h-4 text-blue-600" />
              <span>Objective</span>
            </div>
            <p className="leading-relaxed text-gray-600 pl-6">
              {scheme.description}
            </p>
          </div>

          {/* Key Benefits */}
          <div className="space-y-2">
            <div className="flex items-center space-x-2 text-gray-850 font-bold">
              <FiAward className="w-4 h-4 text-green-600" />
              <span>Benefits Offered</span>
            </div>
            <div className="p-3 bg-green-50/40 border border-green-150/50 rounded-xl text-green-950 font-semibold leading-relaxed ml-6">
              {scheme.benefits || "Monetary and non-monetary assistance provided."}
            </div>
          </div>

          {/* Eligibility Rules Checklist */}
          {((scheme.eligibility_rules && scheme.eligibility_rules.length > 0) || scheme.eligibility) && (
            <div className="space-y-2">
              <div className="flex items-center space-x-2 text-gray-850 font-bold">
                <FiLayers className="w-4 h-4 text-purple-600" />
                <span>Eligibility Criteria</span>
              </div>
              <div className="ml-6 space-y-2">
                {scheme.eligibility_rules ? (
                  scheme.eligibility_rules.map((rule, idx) => (
                    <div key={idx} className="p-2.5 bg-gray-50 border border-gray-100 rounded-xl flex items-start space-x-2 text-gray-700">
                      <span className="w-1.5 h-1.5 bg-purple-500 rounded-full mt-1.5 flex-shrink-0" />
                      <span className="font-medium text-xs leading-relaxed">{rule.description}</span>
                    </div>
                  ))
                ) : (
                  <div className="p-2.5 bg-gray-50 border border-gray-100 rounded-xl text-xs space-y-1">
                    <p>State: <strong>{scheme.eligibility?.state}</strong></p>
                    <p>Gender: <strong>{scheme.eligibility?.gender}</strong></p>
                    {scheme.eligibility?.incomeLimit && <p>Max Income: <strong>₹{scheme.eligibility.incomeLimit}</strong></p>}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Documents Needed */}
          {((scheme.required_documents && scheme.required_documents.length > 0) || (scheme.documentsRequired && scheme.documentsRequired.length > 0)) && (
            <div className="space-y-2">
              <div className="flex items-center space-x-2 text-gray-850 font-bold">
                <FiFileText className="w-4 h-4 text-amber-500" />
                <span>Required Documents</span>
              </div>
              <ul className="ml-6 space-y-1.5">
                {(scheme.required_documents || scheme.documentsRequired).map((doc, idx) => (
                  <li key={idx} className="flex items-center space-x-2 text-xs font-medium text-gray-700">
                    <span className="w-1.5 h-1.5 bg-amber-500 rounded-full flex-shrink-0" />
                    <span>{doc}</span>
                  </li>
                ))}
              </ul>
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
        {applyUrl && (
          <div className="p-4 border-t border-gray-100 bg-gray-50/50 flex-shrink-0">
            <a
              href={applyUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center justify-center space-x-2 text-center w-full py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-bold transition shadow-md hover:shadow-lg cursor-pointer text-sm"
            >
              <span>Apply Directly Online</span>
              <FiExternalLink className="w-4 h-4" />
            </a>
          </div>
        )}
      </div>
    </div>
  );
}
