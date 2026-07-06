import React from 'react';
import { FiCheckCircle, FiAlertCircle, FiAward, FiUserCheck, FiChevronRight } from 'react-icons/fi';
import { useChatStore } from '../../store/useChatStore';

export default function SidebarDashboard({ profileSummary, eligibleSchemes, missingInfo }) {
  const { setSelectedSchemeDetail } = useChatStore();
  const profileKeys = Object.keys(profileSummary || {});
  
  return (
    <div className="w-full flex flex-col space-y-4 h-full overflow-y-auto pr-1">
      
      {/* 1. Profile Traits Verified Card */}
      <div className="bg-white border border-gray-100 rounded-2xl p-4 shadow-sm space-y-2.5">
        <div className="flex items-center space-x-2 text-gray-800 border-b border-gray-50 pb-2">
          <FiUserCheck className="w-4 h-4 text-blue-600" />
          <h3 className="font-bold text-xs">Verified Profile</h3>
        </div>
        {profileKeys.length === 0 ? (
          <p className="text-xs text-gray-400 italic py-1">No traits verified yet. Start conversing to update.</p>
        ) : (
          <div className="grid grid-cols-2 gap-2 max-h-[150px] overflow-y-auto pr-0.5">
            {profileKeys.map((key) => (
              <div key={key} className="p-2 bg-gray-50 border border-gray-100 rounded-lg text-xs">
                <span className="text-gray-400 font-bold uppercase tracking-wider text-[8px] block truncate">
                  {key.replace('_', ' ')}
                </span>
                <span className="text-gray-700 font-semibold truncate block capitalize mt-0.5">
                  {String(profileSummary[key])}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 2. Pending Verification Checklist */}
      <div className="bg-white border border-gray-100 rounded-2xl p-4 shadow-sm space-y-2.5">
        <div className="flex items-center space-x-2 text-gray-800 border-b border-gray-50 pb-2">
          <FiAlertCircle className="w-4 h-4 text-amber-500" />
          <h3 className="font-bold text-xs">Required Data</h3>
        </div>
        {missingInfo.length === 0 ? (
          <div className="flex items-center space-x-2 text-green-600 py-1 text-xs">
            <FiCheckCircle className="w-3.5 h-3.5 flex-shrink-0" />
            <span className="font-semibold">Profile fully completed!</span>
          </div>
        ) : (
          <div className="space-y-1.5 max-h-[150px] overflow-y-auto pr-0.5">
            {missingInfo.map((field) => (
              <div key={field} className="flex items-center justify-between p-2 bg-amber-50/40 border border-amber-100/50 rounded-lg text-xs text-amber-800 font-medium">
                <span className="capitalize">{field.replace('_', ' ')}</span>
                <span className="px-1.5 py-0.5 bg-amber-100/80 text-amber-900 rounded font-bold text-[8px] uppercase tracking-wider">
                  Required
                </span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 3. Eligible Schemes Recommendations */}
      <div className="bg-white border border-gray-100 rounded-2xl p-4 shadow-sm space-y-2.5 flex-1 flex flex-col min-h-[200px]">
        <div className="flex items-center space-x-2 text-gray-800 border-b border-gray-50 pb-2">
          <FiAward className="w-4 h-4 text-green-600" />
          <h3 className="font-bold text-xs">Eligible Schemes ({eligibleSchemes.length})</h3>
        </div>
        {eligibleSchemes.length === 0 ? (
          <div className="flex-1 flex flex-col items-center justify-center text-center p-4 border border-dashed border-gray-100 rounded-xl">
            <p className="text-xs text-gray-400 italic">No recommendations yet.</p>
            <p className="text-[9px] text-gray-450 mt-1 max-w-[150px] leading-relaxed">
              Introduce yourself or submit pending data to receive matches.
            </p>
          </div>
        ) : (
          <div className="space-y-1.5 overflow-y-auto flex-1 max-h-[280px] pr-0.5">
            {eligibleSchemes.map((scheme) => (
              <button
                key={scheme.id || scheme.scheme_id}
                type="button"
                onClick={() => setSelectedSchemeDetail(scheme)}
                className="w-full text-left flex items-center justify-between p-2.5 bg-green-50/20 hover:bg-green-50/60 border border-green-100/40 hover:border-green-300 rounded-xl text-xs text-gray-750 font-medium transition cursor-pointer"
              >
                <div className="flex flex-col space-y-0.5 max-w-[80%]">
                  <span className="font-bold text-gray-800 truncate">{scheme.title || scheme.name}</span>
                  <span className="text-[9px] text-gray-400 capitalize truncate">{scheme.category}</span>
                </div>
                <FiChevronRight className="w-3.5 h-3.5 text-green-600 flex-shrink-0" />
              </button>
            ))}
          </div>
        )}
      </div>

    </div>
  );
}
