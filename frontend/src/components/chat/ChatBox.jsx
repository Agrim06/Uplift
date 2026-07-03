import React, { useEffect, useRef } from 'react';
import MessageBubble from './MessageBubble';
import { FiCompass, FiInfo } from 'react-icons/fi';

const STARTER_SUGGESTIONS = [
  "I am a student from Karnataka looking for higher education scholarships.",
  "What schemes are available for agricultural workers in Maharashtra?",
  "Are there financial assistance schemes for women entrepreneurs?"
];

export default function ChatBox({ messages, isTyping, onSendMessage }) {
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Triggers scroll adjustments on new messages or typing indicator triggers
  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50/50 rounded-2xl border border-gray-100 min-h-[350px]">
      {messages.length === 0 ? (
        <div className="flex flex-col items-center justify-center h-full text-center space-y-6 py-10">
          <div className="w-14 h-14 bg-blue-50 rounded-full flex items-center justify-center text-blue-600">
            <FiCompass className="w-7 h-7" />
          </div>
          <div className="max-w-md space-y-2">
            <h3 className="text-base font-bold text-gray-800 font-sans">Welcome to Scheme Finder</h3>
            <p className="text-xs text-gray-500 leading-relaxed">
              Describe your background (e.g., student, farmer, entrepreneur, state of residence) to receive personalized government scheme suggestions.
            </p>
          </div>
          <div className="w-full max-w-lg space-y-2">
            <p className="text-[10px] font-bold text-gray-400 uppercase tracking-wider text-left pl-1">
              Select a starter prompt:
            </p>
            {STARTER_SUGGESTIONS.map((suggestion) => (
              <button
                key={suggestion}
                type="button"
                onClick={() => onSendMessage(suggestion)}
                className="w-full text-left p-3.5 bg-white border border-gray-100 hover:border-blue-300 rounded-xl text-xs text-gray-700 font-medium transition shadow-sm hover:shadow hover:bg-blue-50/10 cursor-pointer flex items-start space-x-2"
              >
                <FiInfo className="w-3.5 h-3.5 text-blue-500 mt-0.5 flex-shrink-0" />
                <span>{suggestion}</span>
              </button>
            ))}
          </div>
        </div>
      ) : (
        <>
          {messages.map((msg) => (
            <MessageBubble 
              key={msg.id} 
              message={msg} 
              onQuickReply={onSendMessage} 
            />
          ))}

          {/* Typing indicator */}
          {isTyping && (
            <div className="flex justify-start w-full my-2 animate-pulse">
              <div className="flex items-center space-x-2 bg-white border border-gray-100 rounded-2xl p-4 shadow-sm rounded-bl-none text-gray-500 text-xs">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
                <span className="text-[10px] font-bold text-gray-400 pl-2">AI is evaluating profile...</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </>
      )}
    </div>
  );
}
