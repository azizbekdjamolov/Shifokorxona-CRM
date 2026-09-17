import axiosInstance from "./axiosInstance";

export const getDoctorReviews = (doctorId) => axiosInstance.get(`/reviews/doctor/${doctorId}/`);

export const createReview = (data) => axiosInstance.post("/reviews/create/", data);

export const getMyReviews = () => axiosInstance.get("/reviews/my/");

export const getAdminReviews = (params) => axiosInstance.get("/reviews/admin/", { params });

export const moderateReview = (id, data) => axiosInstance.patch(`/reviews/admin/${id}/`, data);