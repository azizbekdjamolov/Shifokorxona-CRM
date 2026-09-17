import axiosInstance from "./axiosInstance";

export const getMyPrescriptions = () => axiosInstance.get("/prescriptions/my/");

export const createPrescription = (data) => axiosInstance.post("/prescriptions/create/", data, {
  headers: { "Content-Type": "multipart/form-data" },
});

export const getMyPrescriptionsAsDoctor = () => axiosInstance.get("/prescriptions/doctor/");

export const getPatientHistory = (params) => axiosInstance.get("/prescriptions/doctor/history/", { params });