import { Link, NavLink } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useAuth } from "./context/AuthContext";
import ThemeToggle from "./components/ThemeToggle";
import LanguageSwitcher from "./components/LanguageSwitcher";
import PublicRoutes from "./routes/PublicRoutes";
import UserRoutes from "./routes/UserRoutes";
import DoctorRoutes from "./routes/DoctorRoutes";
import AdminRoutes from "./routes/AdminRoutes";
import ProfileRoutes from "./routes/ProfileRoutes";

export default function App() {
  const { user, logout } = useAuth();
  const { t } = useTranslation();

  const navLinkClass = ({ isActive }) =>
    isActive ? "nav-link nav-link-active" : "nav-link";

  return (
    <div className="app">
      <header className="app-header">
        <Link to="/" className="brand">
          Shifokorxona CRM
        </Link>
        <nav className="main-nav">
          <NavLink to="/" className={navLinkClass} end>
            {t("nav.home")}
          </NavLink>
          <NavLink to="/doctors" className={navLinkClass}>
            {t("nav.doctors")}
          </NavLink>
          {user?.role === "patient" && (
            <>
              <NavLink to="/dashboard" className={navLinkClass}>
                {t("nav.dashboard")}
              </NavLink>
              <NavLink to="/my-queue" className={navLinkClass}>
                {t("nav.myQueue")}
              </NavLink>
              <NavLink to="/my-prescriptions" className={navLinkClass}>
                {t("nav.myPrescriptions")}
              </NavLink>
            </>
          )}
          {user?.role === "doctor" && (
            <>
              <NavLink to="/doctor" className={navLinkClass}>
                {t("nav.doctorPanel")}
              </NavLink>
              <NavLink to="/doctor/today-queue" className={navLinkClass}>
                {t("nav.todayQueue")}
              </NavLink>
              <NavLink to="/doctor/schedule" className={navLinkClass}>
                {t("nav.schedule")}
              </NavLink>
            </>
          )}
          {user?.role === "admin" && (
            <>
              <NavLink to="/admin" className={navLinkClass}>
                {t("nav.adminPanel")}
              </NavLink>
              <NavLink to="/admin/users" className={navLinkClass}>
                {t("nav.users")}
              </NavLink>
              <NavLink to="/admin/doctors" className={navLinkClass}>
                {t("nav.doctors")}
              </NavLink>
              <NavLink to="/admin/bookings" className={navLinkClass}>
                {t("nav.bookings")}
              </NavLink>
            </>
          )}
          {user && (
            <NavLink to="/profile" className={navLinkClass}>
              {t("nav.profile")}
            </NavLink>
          )}
        </nav>
        <div className="header-actions">
          <ThemeToggle />
          <LanguageSwitcher />
          {user ? (
            <div className="user-menu">
              <span className="user-avatar">
                {(user.full_name || user.email).charAt(0).toUpperCase()}
              </span>
              <span className="user-name">
                {user.full_name || user.email}
                <small className="user-role">{t(`roles.${user.role}`)}</small>
              </span>
              <button className="btn btn-outline btn-sm btn-logout" onClick={logout}>
                {t("nav.logout")}
              </button>
            </div>
          ) : (
            <Link to="/login" className="btn btn-primary btn-sm btn-login">
              {t("auth.login")}
            </Link>
          )}
        </div>
      </header>
      <main className="app-main">
        <PublicRoutes />
        <UserRoutes />
        <DoctorRoutes />
        <AdminRoutes />
        <ProfileRoutes />
      </main>
      <footer className="app-footer">Shifokorxona CRM © 2026</footer>
    </div>
  );
}