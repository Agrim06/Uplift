'use client';

import React from 'react';
import { clsx } from 'clsx';
import { FiAlertTriangle, FiUser, FiCpu } from 'react-icons/fi';

const MISSING_INFO_FIELDS = {
  income: {
    label: "Annual Income",
    prompt: "Please select or enter your annual family income:",
    inputType: "number",
    placeholder: "e.g., 200000",
    choices: [
      { label: "Under ₹2.5 Lakhs", value: "My annual family income is 200000" },
      { label: "₹2.5 Lakhs - ₹5 Lakhs", value: "My annual family income is 350000" },
      { label: "Above ₹5 Lakhs", value: "My annual family income is 600000" }
    ]
  },
  state: {
    label: "Residential State",
    prompt: "Which state are you residing in?",
    inputType: "select",
    options: ["Karnataka", "Maharashtra", "Tamil Nadu", "Delhi", "Uttar Pradesh", "Bihar", "Gujarat"]
  },
  category: {
    label: "Social Category",
    prompt: "Please select your social category:",
    inputType: "select",
    options: ["General", "OBC", "SC", "ST"]
  },
  caste: {
    label: "Social Category",
    prompt: "Please select your social category:",
    inputType: "select",
    options: ["General", "OBC", "SC", "ST"]
  },
  education: {
    label: "Education Level",
    prompt: "Please select your education level:",
    inputType: "select",
    options: ["Class 10", "Class 12", "Undergraduate", "Postgraduate", "Engineering", "Diploma"]
  },
  occupation: {
    label: "Occupation",
    prompt: "Please select your occupation:",
    inputType: "select",
    options: ["Student", "Farmer", "Entrepreneur", "Artisan", "Self-Employed"]
  },
  age: {
    label: "Age",
    prompt: "Please enter your age:",
    inputType: "number",
    placeholder: "e.g., 21"
  },
  gender: {
    label: "Gender",
    prompt: "Please select your gender:",
    inputType: "select",
    options: ["Male", "Female", "Transgender", "Prefer not to say"]
  }
};

export default function MessageBubble({ message, onQuickReply }) {
  const isUser = message.role === 'user';
  const isError = message.role === 'error';

  return (
    <div className={clsx(
      "flex w-full my-2 animate-fade-in",
      isUser ? "justify-end" : "justify-start"
    )}>
      <div className={clsx(
        "flex max-w-[85%] md:max-w-[80%] items-start space-x-2 rounded-2xl p-4 shadow-sm",
        isUser 
          ? "bg-blue-600 text-white rounded-br-none" 
          : isError
            ? "bg-red-50 border border-red-200 text-red-800 rounded-bl-none"
            : "bg-white border border-gray-100 text-gray-800 rounded-bl-none"
      )}>
        {/* User/AI Icons */}
        <div className="flex-shrink-0 mt-0.5">
          {isUser ? (
            <FiUser className="w-4 h-4 text-blue-200" />
          ) : isError ? (
            <FiAlertTriangle className="w-4 h-4 text-red-500" />
          ) : (
            <FiCpu className="w-4 h-4 text-blue-600" />
          )}
        </div>

        {/* Content & Actionable Missing Info Prompts */}
        <div className="flex-1 space-y-3 overflow-hidden">
          <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>

          {/* Inline input selector handles missing info keys - shown one by one */}
          {!isUser && message.missingInfoForm && message.missingInfoForm.length > 0 && (
            <div className="mt-3 p-3.5 bg-gray-50 border border-gray-150 rounded-xl space-y-4 text-gray-700">
              {message.missingInfoForm.slice(0, 1).map((fieldKey) => {
                const config = MISSING_INFO_FIELDS[fieldKey];
                if (!config) return null;

                return (
                  <div key={fieldKey} className="space-y-2 border-b border-gray-150 last:border-b-0 pb-3 last:pb-0">
                    <p className="text-[10px] font-bold text-gray-400 uppercase tracking-wider">
                      Pending Parameter: {config.label}
                    </p>
                    <p className="text-xs font-semibold text-gray-800">{config.prompt}</p>

                    {/* Selector Chips */}
                    {config.choices && (
                      <div className="flex flex-wrap gap-1.5 pt-1">
                        {config.choices.map((choice) => (
                          <button
                            key={choice.label}
                            type="button"
                            onClick={() => onQuickReply(choice.value)}
                            className="px-2.5 py-1 bg-white hover:bg-blue-50 border border-gray-200 hover:border-blue-500 hover:text-blue-600 text-xs font-medium rounded-full transition shadow-sm cursor-pointer"
                          >
                            {choice.label}
                          </button>
                        ))}
                      </div>
                    )}

                    {/* Standard Number Form Submission */}
                    {config.inputType === 'number' && (
                      <form 
                        onSubmit={(e) => {
                          e.preventDefault();
                          const val = e.target.elements[fieldKey].value;
                          if (val) {
                            onQuickReply(`My annual income is ${val}`);
                          }
                        }}
                        className="flex items-center space-x-2 pt-2"
                      >
                        <input
                          name={fieldKey}
                          type="number"
                          placeholder={config.placeholder || "Enter exact amount in ₹"}
                          className="px-3 py-1.5 border border-gray-200 rounded-lg text-xs w-44 focus:outline-none focus:border-blue-500 bg-white text-gray-800 shadow-xs"
                          required
                        />
                        <button
                          type="submit"
                          className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs rounded-lg transition shadow-xs cursor-pointer"
                        >
                          Submit Income
                        </button>
                      </form>
                    )}

                    {/* Standard Dropdown Selectors */}
                    {config.inputType === 'select' && !config.choices && (
                      <div className="flex flex-wrap gap-1.5 pt-1">
                        {config.options.map((option) => (
                          <button
                            key={option}
                            type="button"
                            onClick={() => onQuickReply(`My ${config.label.toLowerCase()} is ${option}`)}
                            className="px-2.5 py-1 bg-white hover:bg-blue-50 border border-gray-200 hover:border-blue-500 hover:text-blue-600 text-xs font-medium rounded-full transition shadow-sm cursor-pointer"
                          >
                            {option}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
