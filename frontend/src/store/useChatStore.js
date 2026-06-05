import { create } from 'zustand';

export const useChatStore = create((set) => ({
    messages : [],
    profileSummary : {},
    eligibleSchemes : [],
    missingInfo : [],
    isTyping : false,

    addMessage: (message) => set((state) => ({
        message: [...state.messages, message]
    })),

    updateAPIResponse: (data) => set((state) => ({
        profileSummary: data.profile_summary,
        eligibleSchemes: data.eligible_schemes,
        missingInfo: data.missing_info,
        isTyping: false
    })), 

    setTyping: (status) => set({isTyping : status}),
}));