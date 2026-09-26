import axiosInstance from "./axiosInstance";

export const getAiMessages = () => axiosInstance.get("/ai/messages/");

export const sendAiMessage = ({ message = "", image = null, language = "uz" }) => {
  const form = new FormData();
  form.append("message", message);
  form.append("language", language);
  if (image) {
    form.append("image", image);
  }
  return axiosInstance.post("/ai/chat/", form);
};