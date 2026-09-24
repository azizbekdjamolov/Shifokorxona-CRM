import { Navigate, Outlet, Route, Routes } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import Profile from "../pages/Profile";

function Guard() {
  const { user, loading } = useAuth();
  if (loading) return <p>Yuklanmoqda...</p>;
  if (!user) return <Navigate to="/" replace />;
  return <Outlet />;
}

export default function ProfileRoutes() {
  return (
    <Routes>
      <Route element={<Guard />}>
        <Route path="/profile" element={<Profile />} />
      </Route>
    </Routes>
  );
}