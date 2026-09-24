import { Navigate, Outlet, Route, Routes } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import UserDashboard from "../pages/user/UserDashboard";
import MyQueue from "../pages/user/MyQueue";
import MyPrescriptions from "../pages/user/MyPrescriptions";
import MyPayments from "../pages/user/MyPayments";
import LeaveReview from "../pages/user/LeaveReview";

function Guard() {
  const { user, loading } = useAuth();
  if (loading) return <p>Yuklanmoqda...</p>;
  if (!user) return <Navigate to="/" replace />;
  if (user.role !== "patient") return <Navigate to="/" replace />;
  return <Outlet />;
}

export default function UserRoutes() {
  return (
    <Routes>
      <Route element={<Guard />}>
        <Route path="/dashboard" element={<UserDashboard />} />
        <Route path="/my-queue" element={<MyQueue />} />
        <Route path="/my-prescriptions" element={<MyPrescriptions />} />
        <Route path="/my-payments" element={<MyPayments />} />
        <Route path="/leave-review/:bookingId" element={<LeaveReview />} />
      </Route>
    </Routes>
  );
}