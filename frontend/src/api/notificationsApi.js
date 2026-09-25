import axiosInstance from "./axiosInstance";

export const getTelegramLinkCode = () => axiosInstance.get("/notifications/telegram/link-code/");

export const confirmTelegramLink = (code) => axiosInstance.post("/notifications/telegram/confirm/", { code });

export const unlinkTelegram = () => axiosInstance.post("/notifications/telegram/unlink/");