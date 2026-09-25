import { Navigate, Outlet, Route, Routes } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import Home from "../pages/public/Home";
import DoctorsList from "../pages/public/DoctorsList";
import SpecialtyPage from "../pages/public/SpecialtyPage";
import DoctorDetailPage from "../pages/public/DoctorDetailPage";
import LoginPage from "../pages/auth/LoginPage";
import RegisterPage from "../pages/auth/RegisterPage";
import ForgotPasswordPage from "../pages/auth/ForgotPasswordPage";
import ChatPage from "../pages/ChatPage";
import UserDashboard from "../pages/user/UserDashboard";
import MyQueue from "../pages/user/MyQueue";
import MyPrescriptions from "../pages/user/MyPrescriptions";
import LeaveReview from "../pages/user/LeaveReview";
import DoctorDashboard from "../pages/doctor/DoctorDashboard";
import TodayQueue from "../pages/doctor/TodayQueue";
import AddPrescription from "../pages/doctor/AddPrescription";
import Schedule from "../pages/doctor/Schedule";
import AdminDashboard from "../pages/admin/AdminDashboard";
import ManageUsers from "../pages/admin/ManageUsers";
import ManageDoctors from "../pages/admin/ManageDoctors";
import ManageSpecialties from "../pages/admin/ManageSpecialties";
import ManageBookings from "../pages/admin/ManageBookings";
import ManageReviews from "../pages/admin/ManageReviews";
import Profile from "../pages/Profile";

function PatientGuard() {
  const { user, loading } = useAuth();
  if (loading) return <p>Yuklanmoqda...</p>;
  if (!user) return <Navigate to="/login" replace />;
  if (user.role !== "patient") return <Navigate to="/" replace />;
  return <Outlet />;
}

function DoctorGuard() {
  const { user, loading } = useAuth();
  if (loading) return <p>Yuklanmoqda...</p>;
  if (!user) return <Navigate to="/login" replace />;
  if (user.role !== "doctor") return <Navigate to="/" replace />;
  return <Outlet />;
}

function AdminGuard() {
  const { user, loading } = useAuth();
  if (loading) return <p>Yuklanmoqda...</p>;
  if (!user) return <Navigate to="/login" replace />;
  if (user.role !== "admin") return <Navigate to="/" replace />;
  return <Outlet />;
}

function ProfileGuard() {
  const { user, loading } = useAuth();
  if (loading) return <p>Yuklanmoqda...</p>;
  if (!user) return <Navigate to="/login" replace />;
  return <Outlet />;
}

function AuthenticatedGuard() {
  const { user, loading } = useAuth();
  if (loading) return <p>Yuklanmoqda...</p>;
  if (!user) return <Navigate to="/login" replace />;
  return <Outlet />;
}

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/doctors" element={<DoctorsList />} />
      <Route path="/doctors/:id" element={<DoctorDetailPage />} />
      <Route path="/specialties/:slug" element={<SpecialtyPage />} />
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/forgot-password" element={<ForgotPasswordPage />} />

      <Route element={<AuthenticatedGuard />}>
        <Route path="/messages" element={<ChatPage />} />
      </Route>

      <Route element={<PatientGuard />}>
        <Route path="/dashboard" element={<UserDashboard />} />
        <Route path="/my-queue" element={<MyQueue />} />
        <Route path="/my-prescriptions" element={<MyPrescriptions />} />
        <Route path="/leave-review/:bookingId" element={<LeaveReview />} />
      </Route>

      <Route element={<DoctorGuard />}>
        <Route path="/doctor" element={<DoctorDashboard />} />
        <Route path="/doctor/today-queue" element={<TodayQueue />} />
        <Route path="/doctor/add-prescription" element={<AddPrescription />} />
        <Route path="/doctor/schedule" element={<Schedule />} />
      </Route>

      <Route element={<AdminGuard />}>
        <Route path="/admin" element={<AdminDashboard />} />
        <Route path="/admin/users" element={<ManageUsers />} />
        <Route path="/admin/doctors" element={<ManageDoctors />} />
        <Route path="/admin/specialties" element={<ManageSpecialties />} />
        <Route path="/admin/bookings" element={<ManageBookings />} />
        <Route path="/admin/reviews" element={<ManageReviews />} />
      </Route>

      <Route element={<ProfileGuard />}>
        <Route path="/profile" element={<Profile />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}