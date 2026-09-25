import axiosInstance from "./axiosInstance";

export const getDoctors = (params) => axiosInstance.get("/doctors/", { params });

export const getDoctor = (id) => axiosInstance.get(`/doctors/${id}/`);

export const getSpecialties = () => axiosInstance.get("/doctors/specialties/");

export const getDoctorMe = () => axiosInstance.get("/doctors/me/");

export const getMySchedule = () => axiosInstance.get("/doctors/me/schedule/");

export const addSchedule = (data) => axiosInstance.post("/doctors/me/schedule/", data);

export const updateSchedule = (id, data) => axiosInstance.patch(`/doctors/me/schedule/${id}/`, data);

export const deleteSchedule = (id) => axiosInstance.delete(`/doctors/me/schedule/${id}/`);

export const createDoctor = (data) => axiosInstance.post("/doctors/create/", data, {
  headers: { "Content-Type": "multipart/form-data" },
});

export const updateDoctor = (id, data) => axiosInstance.patch(`/doctors/${id}/update/`, data, {
  headers: { "Content-Type": "multipart/form-data" },
});

export const updateDoctorMe = (data) => axiosInstance.patch("/doctors/me/", data, {
  headers: { "Content-Type": "multipart/form-data" },
});

export const getAdminDoctors = (params) => axiosInstance.get("/doctors/admin/", { params });

export const toggleDoctor = (id, data) => axiosInstance.patch(`/doctors/admin/${id}/toggle/`, data);

export const createSpecialty = (data) => axiosInstance.post("/doctors/specialties/create/", data);

export const updateSpecialty = (id, data) => axiosInstance.patch(`/doctors/specialties/${id}/`, data);

export const deleteSpecialty = (id) => axiosInstance.delete(`/doctors/specialties/${id}/delete/`);