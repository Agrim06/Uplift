import React, { useRef, useEffect } from 'react';
import { useChatStore } from '../store/useChatStore';
import chatService from '../services/chatService';
import ChatBox from '../components/chat/ChatBox';
import InputBar from '../components/chat/InputBar';
import SidebarDashboard from '../components/chat/SidebarDashboard';
import { toast } from 'react-hot-toast';

export default function Chat() {
  const {
    messages,
    profileSummary,
    eligibleSchemes,
    missingInfo,
    isTyping,
    addMessage,
    updateAPIResponse,
    setTyping,
    setError,
    clearChat
  } = useChatStore();

  const abortControllerRef = useRef(null);

  // Terminate any unresolved API processing if component unmounts
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  const handleSendMessage = async (text) => {
    // 1. Instantly append User's message in the thread
    addMessage({ role: 'user', content: text });
    setTyping(true);

    // Cancel prior pending requests
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    abortControllerRef.current = new AbortController();

    try {
      const response = await chatService.sendChatMessage(text, {
        signal: abortControllerRef.current.signal
      });

      // 2. Extract agent reply content from structured reflection packet
      const agentReply = response.reflection?.agent_reply || response.message || 'I have updated your recommendations.';
      
      // 3. Append AI message to list, keeping missing traits keys inline
      addMessage({
        role: 'ai',
        content: agentReply,
        missingInfoForm: response.missing_info || []
      });

      // 4. Set dashboard values (Traits list, recommendations list, checking criteria)
      updateAPIResponse(response);

      // Trigger user toast notice if missing parameters occur
      if (response.missing_info && response.missing_info.length > 0) {
        toast.success(`Please complete the pending required fields.`, {
          icon: '📝',
          duration: 3500
        });
      }
    } catch (err) {
      // Gracefully ignore user cancellations
      if (err.name === 'CanceledError' || err.code === 'ERR_CANCELED') {
        return;
      }
      
      // 5. Manage failures, push detailed error description bubble
      const errMsg = err.message || 'Failed to communicate with recommendation server.';
      setError(errMsg);
      toast.error(errMsg);

      addMessage({
        role: 'error',
        content: `Error details: ${errMsg}. Please click to retry or send a new prompt.`
      });
    }
  };

  const handleCancelRequest = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
      setTyping(false);
      toast.error("Query cancelled.");
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-4 md:py-6 flex flex-col md:flex-row gap-5 h-[calc(100vh-80px)] overflow-hidden">
      {/* Primary chat scroll container */}
      <div className="flex-1 flex flex-col h-full bg-white border border-gray-100 rounded-3xl p-4 md:p-5 shadow-sm overflow-hidden">
        
        {/* Chat Panel Header */}
        <div className="flex justify-between items-center border-b border-gray-100 pb-3 mb-4 flex-shrink-0">
          <div>
            <h1 className="text-lg font-bold text-gray-800">Agentic Recommendation Assistant</h1>
            <p className="text-[10px] text-gray-400">Describe your profile in natural language to find matching schemes</p>
          </div>
          <button 
            type="button"
            onClick={clearChat}
            className="text-xs text-red-500 hover:text-red-600 hover:bg-red-50/50 border border-red-100 px-3 py-1.5 rounded-xl font-semibold transition cursor-pointer"
          >
            Reset
          </button>
        </div>

        {/* Scroll Window */}
        <ChatBox 
          messages={messages} 
          isTyping={isTyping} 
          onSendMessage={handleSendMessage} 
        />

        {/* Text Input Panel */}
        <div className="pt-4 flex-shrink-0">
          <InputBar 
            onSendMessage={handleSendMessage} 
            isTyping={isTyping} 
            onCancelRequest={handleCancelRequest} 
          />
        </div>
      </div>

      {/* Side Status Dashboard (collapses on mobile below the main panel if no flex-shrink is defined) */}
      <div className="w-full md:w-72 lg:w-80 flex-shrink-0 h-full overflow-hidden flex flex-col pb-4 md:pb-0">
        <SidebarDashboard 
          profileSummary={profileSummary} 
          eligibleSchemes={eligibleSchemes} 
          missingInfo={missingInfo} 
        />
      </div>
    </div>
  );
}
