import React, { useState, useRef, useEffect } from 'react';
import { FiSend, FiXCircle } from 'react-icons/fi';

export default function InputBar({ onSendMessage, isTyping, onCancelRequest }) {
  const [text, setText] = useState('');
  const textareaRef = useRef(null);

  const handleSend = (e) => {
    e.preventDefault();
    if (!text.trim() || isTyping) return;
    onSendMessage(text.trim());
    setText('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend(e);
    }
  };

  // Adjust input text area dimensions relative to input length
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  }, [text]);

  return (
    <form onSubmit={handleSend} className="flex items-end space-x-2 bg-white border border-gray-200 rounded-2xl p-2 shadow-sm focus-within:border-blue-400 focus-within:ring-1 focus-within:ring-blue-100 transition">
      <textarea
        ref={textareaRef}
        rows={1}
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={isTyping ? "Please wait for AI response..." : "Type details or respond to AI prompts..."}
        disabled={isTyping}
        className="flex-1 resize-none border-0 focus:ring-0 focus:outline-none text-xs text-gray-800 placeholder-gray-400 py-2.5 px-3 min-h-[38px] max-h-[120px] bg-transparent"
      />
      <div className="flex items-center space-x-1 pb-1 pr-1">
        {isTyping ? (
          <button
            type="button"
            onClick={onCancelRequest}
            title="Cancel request"
            className="p-2 text-red-500 hover:bg-red-50 rounded-xl transition cursor-pointer"
          >
            <FiXCircle className="w-5 h-5" />
          </button>
        ) : (
          <button
            type="submit"
            disabled={!text.trim()}
            className="p-2 bg-blue-600 disabled:bg-gray-50 text-white disabled:text-gray-400 rounded-xl transition hover:bg-blue-700 shadow-sm disabled:shadow-none cursor-pointer"
          >
            <FiSend className="w-4 h-4" />
          </button>
        )}
      </div>
    </form>
  );
}
