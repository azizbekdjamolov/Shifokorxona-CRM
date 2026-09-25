import axiosInstance from "./axiosInstance";

export const getConversations = () => axiosInstance.get("/chats/conversations/");

export const getUnreadConversations = () => axiosInstance.get("/chats/conversations/unread/");

export const openConversation = (doctorId) => axiosInstance.post("/chats/conversations/", { doctor: doctorId });

export const getConversation = (id) => axiosInstance.get(`/chats/conversations/${id}/`);

export const getConversationMessages = (id) => axiosInstance.get(`/chats/conversations/${id}/messages/`);

export const sendMessage = (id, text) => axiosInstance.post(`/chats/conversations/${id}/messages/`, { text });