import { Navigate, Outlet, Route, Routes } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import DoctorDashboard from "../pages/doctor/DoctorDashboard";
import TodayQueue from "../pages/doctor/TodayQueue";
import AddPrescription from "../pages/doctor/AddPrescription";
import Schedule from "../pages/doctor/Schedule";

function Guard() {
  const { user, loading } = useAuth();
  if (loading) return <p>Yuklanmoqda...</p>;
  if (!user) return <Navigate to="/" replace />;
  if (user.role !== "doctor") return <Navigate to="/" replace />;
  return <Outlet />;
}

export default function DoctorRoutes() {
  return (
    <Routes>
      <Route element={<Guard />}>
        <Route path="/doctor" element={<DoctorDashboard />} />
        <Route path="/doctor/today-queue" element={<TodayQueue />} />
        <Route path="/doctor/add-prescription" element={<AddPrescription />} />
        <Route path="/doctor/schedule" element={<Schedule />} />
      </Route>
    </Routes>
  );
}