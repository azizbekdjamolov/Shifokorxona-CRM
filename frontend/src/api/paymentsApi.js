import axiosInstance from "./axiosInstance";

export const getMyPayments = () => axiosInstance.get("/payments/");

export const getPaymentProviders = () => axiosInstance.get("/payments/providers/");

export const initiatePayment = (bookingId, provider) =>
  axiosInstance.post("/payments/initiate/", { booking: bookingId, provider });

export const mockPay = (id) => axiosInstance.post(`/payments/${id}/mock-pay/`);

export const cancelPayment = (id) => axiosInstance.post(`/payments/${id}/cancel/`);