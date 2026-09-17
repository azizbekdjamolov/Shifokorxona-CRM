import { Navigate, Route, Routes } from "react-router-dom";
import Home from "../pages/public/Home";
import DoctorsList from "../pages/public/DoctorsList";
import SpecialtyPage from "../pages/public/SpecialtyPage";

export default function PublicRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/doctors" element={<DoctorsList />} />
      <Route path="/specialties/:slug" element={<SpecialtyPage />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}