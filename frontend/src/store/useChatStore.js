import { create } from 'zustand';

export const useChatStore = create((set) => ({
    messages : [],
    profileSummary : {},
    eligibleSchemes : [],
    missingInfo : [],
    isTyping : false,
    error: null,

    addMessage: (message) => set((state) => ({
        message: [...state.messages,{
            ...message,
            id: message.id || Date.now().toString(),
            timestamp: new Date()
            }    
        ]
    })),

    updateAPIResponse: (data) => set((state) => ({
        profileSummary: data.profile_summary,
        eligibleSchemes: data.eligible_schemes,
        missingInfo: data.missing_info,
        isTyping: false,
        error: null,
    })), 

    setTyping: (status) => set({isTyping : status}),
    setError: (error) => set({error, isTyping: false}),
    clearChat: () => set({
        messages: [], 
        profileSummary: {}, 
        eligibleSchemes: [], 
        missingInfo: [], 
        error: null, 
        isTyping: false 
    })
}));