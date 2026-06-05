import { useChatStore } from '../store/useChatStore';
import { sendChatMessage } from '../services/chatService';

export const useChat = () => {
    const { addMessage, updateAIResponse, setTyping } = useChatStore();

    const sendMessage = async (text) => {
        addMessage({ role: 'user', content: text });
        setTyping(true);

        try {
            const response = await sendChatMessage(text);

            addMessage({ role: 'ai', content: response.reflection.agent_reply || 'I found some schemes for you.' });
            updateAIResponse(response);
        } catch (error) {
            addMessage({ role: 'error', content: 'Failed to communicate with the server.' });
        } finally {
            setTyping(false);
        }
    };
    return { sendMessage };
};