import axiosInstance from "./axiosInstance";

export const getDoctors = (params) => axiosInstance.get("/doctors/", { params });

export const getDoctor = (id) => axiosInstance.get(`/doctors/${id}/`);

export const getSpecialties = () => axiosInstance.get("/doctors/specialties/");

export const getDoctorMe = () => axiosInstance.get("/doctors/me/");

export const getMySchedule = () => axiosInstance.get("/doctors/me/schedule/");

export const addSchedule = (data) => axiosInstance.post("/doctors/me/schedule/", data);

export const updateSchedule = (id, data) => axiosInstance.patch(`/doctors/me/schedule/${id}/`, data);

export const deleteSchedule = (id) => axiosInstance.delete(`/doctors/me/schedule/${id}/`);

export const createDoctor = (data) => axiosInstance.post("/doctors/create/", data);

export const updateDoctor = (id, data) => axiosInstance.patch(`/doctors/${id}/update/`, data);