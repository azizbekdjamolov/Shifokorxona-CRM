import { Navigate, Outlet, Route, Routes } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import AdminDashboard from "../pages/admin/AdminDashboard";
import ManageUsers from "../pages/admin/ManageUsers";
import ManageDoctors from "../pages/admin/ManageDoctors";
import ManageSpecialties from "../pages/admin/ManageSpecialties";
import ManageBookings from "../pages/admin/ManageBookings";

function Guard() {
  const { user, loading } = useAuth();
  if (loading) return <p>Yuklanmoqda...</p>;
  if (!user) return <Navigate to="/" replace />;
  if (user.role !== "admin") return <Navigate to="/" replace />;
  return <Outlet />;
}

export default function AdminRoutes() {
  return (
    <Routes>
      <Route element={<Guard />}>
        <Route path="/admin" element={<AdminDashboard />} />
        <Route path="/admin/users" element={<ManageUsers />} />
        <Route path="/admin/doctors" element={<ManageDoctors />} />
        <Route path="/admin/specialties" element={<ManageSpecialties />} />
        <Route path="/admin/bookings" element={<ManageBookings />} />
      </Route>
    </Routes>
  );
}