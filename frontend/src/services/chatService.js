import api from "./api";

/**
 * Chat service for interacting with the Agentic AI recommender backend.
 */
const chatService = {
  /**
   * Send a chat message to the Agentic recommender system.
   * 
   * @param {string} messageText - The user message text.
   * @param {Object} [options] - Optional configurations.
   * @param {string} [options.sessionId] - Optional session ID to persist chat context.
   * @param {Array<Object>} [options.history] - Optional chat history/messages for conversational context.
   * @param {AbortSignal} [options.signal] - Abort controller signal to cancel the request.
   * @param {number} [options.timeout] - Override request timeout in milliseconds (defaults to 30000ms/30s for Agentic processing).
   * @returns {Promise<Object>} The normalized response message.
   */
  sendChatMessage: async (messageText, options = {}) => {
    const { sessionId, history, signal, timeout = 30000, existing_profile, ...restOptions } = options;
    
    const payload = {
      message: messageText,
      ...(sessionId && { session_id: sessionId }),
      ...(history && { history }),
      ...(existing_profile && { existing_profile }),
    };

    return api.post('/chat/', payload, {
      signal,
      timeout,
      ...restOptions,
    });
  },
};

// Backward-compatible individual named export
export const sendChatMessage = chatService.sendChatMessage;

export default chatService;
