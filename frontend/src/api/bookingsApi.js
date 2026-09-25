import axiosInstance from "./axiosInstance";

export const getMyBookings = () => axiosInstance.get("/bookings/my/");

export const createBooking = (data) => axiosInstance.post("/bookings/my/", data);

export const cancelMyBooking = (id) => axiosInstance.patch(`/bookings/my/${id}/cancel/`);

export const getDoctorTodayQueue = () => axiosInstance.get("/bookings/doctor/today/");

export const getDoctorBookings = () => axiosInstance.get("/bookings/doctor/");

export const updateBookingStatus = (id, data) => axiosInstance.patch(`/bookings/${id}/`, data);

export const getAdminBookings = (params) => axiosInstance.get("/bookings/admin/", { params });