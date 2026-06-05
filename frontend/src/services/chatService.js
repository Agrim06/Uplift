import api from "./api";

export const sendChatMessage = async (messageText) => {
    const response = await api.post('/chat/' , {message: messageText});
    return response.data;
};
