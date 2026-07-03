import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import schemeService from '../services/schemeService';
import { FiSearch, FiSliders, FiFileText } from 'react-icons/fi';
import { toast } from 'react-hot-toast';

export default function Explorer() {
  const [searchParams] = useSearchParams();
  const schemeIdParam = searchParams.get('id');

  const [schemes, setSchemes] = useState([]);
  const [selectedScheme, setSelectedScheme] = useState(null);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');

  // Loads scheme listings
  useEffect(() => {
    async function loadSchemes() {
      setLoading(true);
      try {
        const response = await schemeService.getSchemes({ search });
        setSchemes(response.items || []);
      } catch (err) {
        console.error(err);
        toast.error("Failed to load schemes.");
      } finally {
        setLoading(false);
      }
    }
    loadSchemes();
  }, [search]);

  // Resolves detail view when query param matches
  useEffect(() => {
    async function loadDetail() {
      if (!schemeIdParam) {
        setSelectedScheme(null);
        return;
      }
      try {
        const detail = await schemeService.getSchemeById(schemeIdParam);
        setSelectedScheme(detail);
      } catch (err) {
        console.error(err);
        toast.error("Failed to load scheme details.");
      }
    }
    loadDetail();
  }, [schemeIdParam]);

  return (
    <div className="max-w-7xl mx-auto px-4 py-6 flex flex-col md:flex-row gap-6 h-[calc(100vh-80px)] overflow-hidden">
      
      {/* List views */}
      <div className="flex-1 bg-white border border-gray-100 rounded-3xl p-5 shadow-sm flex flex-col h-full overflow-hidden">
        <div className="space-y-4 mb-4 flex-shrink-0">
          <div>
            <h1 className="text-xl font-bold text-gray-800">Schemes Directory</h1>
            <p className="text-xs text-gray-400 font-medium">Browse central and state scheme guidelines</p>
          </div>
          
          <div className="flex items-center space-x-2 bg-gray-50 border border-gray-200 rounded-2xl p-2 shadow-sm">
            <FiSearch className="w-4 h-4 text-gray-400 ml-1.5 flex-shrink-0" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by keywords, ministry, category..."
              className="flex-1 bg-transparent border-0 focus:ring-0 focus:outline-none text-xs text-gray-800 placeholder-gray-400 py-1"
            />
          </div>
        </div>

        <div className="flex-1 overflow-y-auto space-y-2 pr-1">
          {loading ? (
            <div className="text-center py-12 text-xs text-gray-400">Loading schemes...</div>
          ) : schemes.length === 0 ? (
            <div className="text-center py-12 text-xs text-gray-400 italic">No schemes found matching criteria.</div>
          ) : (
            schemes.map((scheme) => (
              <button
                key={scheme.id}
                type="button"
                onClick={() => setSelectedScheme(scheme)}
                className={`w-full text-left p-4 rounded-2xl border transition flex flex-col space-y-1.5 cursor-pointer ${
                  selectedScheme?.id === scheme.id
                    ? 'border-blue-400 bg-blue-50/10'
                    : 'border-gray-100 hover:border-blue-200 bg-white'
                }`}
              >
                <div className="flex justify-between items-start">
                  <span className="font-bold text-sm text-gray-800 leading-tight">{scheme.title}</span>
                  <span className="text-[9px] font-bold text-blue-600 bg-blue-50 px-2 py-0.5 rounded-full capitalize">
                    {scheme.category || 'General'}
                  </span>
                </div>
                <p className="text-xs text-gray-400 line-clamp-2 leading-relaxed">{scheme.description}</p>
                <div className="flex items-center text-[10px] text-gray-400 font-semibold space-x-4 pt-1">
                  <span>{scheme.ministry}</span>
                  <span>State: {scheme.eligibility?.state}</span>
                </div>
              </button>
            ))
          )}
        </div>
      </div>

      {/* Description view */}
      <div className="w-full md:w-96 flex-shrink-0 bg-white border border-gray-100 rounded-3xl p-5 shadow-sm flex flex-col h-full overflow-hidden">
        {selectedScheme ? (
          <div className="flex flex-col h-full overflow-y-auto space-y-4 pr-1">
            <div className="space-y-1 border-b border-gray-100 pb-3">
              <span className="text-[10px] text-blue-600 font-bold uppercase tracking-wider">
                {selectedScheme.ministry}
              </span>
              <h2 className="text-base font-extrabold text-gray-800 leading-tight">{selectedScheme.title}</h2>
            </div>

            <div className="space-y-3 text-xs leading-relaxed text-gray-600">
              <div className="space-y-1">
                <span className="font-bold text-gray-800 block text-xs">Description</span>
                <p>{selectedScheme.description}</p>
              </div>

              <div className="space-y-1">
                <span className="font-bold text-gray-800 block text-xs">Key Benefits</span>
                <p className="p-3 bg-green-50/30 border border-green-150/40 text-green-950 rounded-xl font-semibold">
                  {selectedScheme.benefits || "Details of monetary/non-monetary benefits."}
                </p>
              </div>

              <div className="space-y-2">
                <span className="font-bold text-gray-800 block text-xs">Eligibility Requirements</span>
                <div className="p-3 bg-gray-50 border border-gray-100 rounded-xl space-y-2 text-[11px]">
                  <div className="flex justify-between">
                    <span className="text-gray-400 font-medium">State Residence</span>
                    <span className="font-bold text-gray-700">{selectedScheme.eligibility?.state}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400 font-medium">Gender</span>
                    <span className="font-bold text-gray-700">{selectedScheme.eligibility?.gender}</span>
                  </div>
                  {(selectedScheme.eligibility?.minAge || selectedScheme.eligibility?.maxAge) && (
                    <div className="flex justify-between">
                      <span className="text-gray-400 font-medium">Age Bracket</span>
                      <span className="font-bold text-gray-700">
                        {selectedScheme.eligibility.minAge || 0} - {selectedScheme.eligibility.maxAge || 'No limit'} years
                      </span>
                    </div>
                  )}
                  {selectedScheme.eligibility?.incomeLimit && (
                    <div className="flex justify-between">
                      <span className="text-gray-400 font-medium">Max Annual Income</span>
                      <span className="font-bold text-gray-700">₹{selectedScheme.eligibility.incomeLimit}</span>
                    </div>
                  )}
                </div>
              </div>

              {selectedScheme.documentsRequired?.length > 0 && (
                <div className="space-y-1.5">
                  <span className="font-bold text-gray-800 block text-xs">Documents Needed</span>
                  <ul className="space-y-1">
                    {selectedScheme.documentsRequired.map((doc, idx) => (
                      <li key={idx} className="flex items-center space-x-2 text-[11px] font-medium text-gray-700">
                        <FiFileText className="w-3.5 h-3.5 text-blue-500 flex-shrink-0" />
                        <span>{doc}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="flex-1 flex flex-col items-center justify-center text-center p-6 border border-dashed border-gray-100 rounded-2xl">
            <FiSliders className="w-9 h-9 text-gray-350 mb-2" />
            <h3 className="text-xs font-bold text-gray-500">No Scheme Selected</h3>
            <p className="text-[10px] text-gray-405 mt-1 max-w-[150px] leading-relaxed">
              Select a scheme from the directory list to examine complete details and eligibility criteria.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
