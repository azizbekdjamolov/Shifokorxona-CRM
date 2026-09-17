import axiosInstance from "./axiosInstance";

export const register = (data) => axiosInstance.post("/users/register/", data);

export const verifyOtp = (data) => axiosInstance.post("/users/verify-otp/", data);

export const resendOtp = (email) => axiosInstance.post("/users/resend-otp/", { email });

export const getMe = () => axiosInstance.get("/users/me/");

export const updateMe = (data) => axiosInstance.patch("/users/me/", data);

export const login = (data) => axiosInstance.post("/token/", data);

export const getAdminUsers = (params) => axiosInstance.get("/users/admin/", { params });

export const updateAdminUser = (id, data) => axiosInstance.patch(`/users/admin/${id}/`, data);