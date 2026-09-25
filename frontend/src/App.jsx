import { useState } from "react";
import { Link, NavLink } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useAuth } from "./context/AuthContext";
import ThemeToggle from "./components/ThemeToggle";
import LanguageSwitcher from "./components/LanguageSwitcher";
import AppRoutes from "./routes/AppRoutes";

export default function App() {
  const { user, logout } = useAuth();
  const { t } = useTranslation();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const navLinkClass = ({ isActive }) =>
    isActive ? "sidebar-link sidebar-link-active" : "sidebar-link";

  const closeSidebar = () => setSidebarOpen(false);

  return (
    <div className="app">
      <header className="app-header">
        <button
          className="sidebar-toggle"
          aria-label="Menu"
          onClick={() => setSidebarOpen((v) => !v)}
        >
          ☰
        </button>
        <Link to="/" className="brand" onClick={closeSidebar}>
          Shifokorxona CRM
        </Link>
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

      <div className="app-body">
        <aside className={`sidebar ${sidebarOpen ? "sidebar-open" : ""}`}>
          <nav className="sidebar-nav" onClick={closeSidebar}>
            <NavLink to="/" className={navLinkClass} end>
              {t("nav.home")}
            </NavLink>
            <NavLink to="/doctors" className={navLinkClass}>
              {t("nav.doctors")}
            </NavLink>

            {user?.role === "patient" && (
              <div className="sidebar-group">
                <span className="sidebar-label">{t("roles.patient")}</span>
                <NavLink to="/dashboard" className={navLinkClass}>
                  {t("nav.dashboard")}
                </NavLink>
                <NavLink to="/my-queue" className={navLinkClass}>
                  {t("nav.myQueue")}
                </NavLink>
                <NavLink to="/my-prescriptions" className={navLinkClass}>
                  {t("nav.myPrescriptions")}
                </NavLink>
              </div>
            )}

            {user?.role === "doctor" && (
              <div className="sidebar-group">
                <span className="sidebar-label">{t("roles.doctor")}</span>
                <NavLink to="/doctor" className={navLinkClass}>
                  {t("nav.doctorPanel")}
                </NavLink>
                <NavLink to="/doctor/today-queue" className={navLinkClass}>
                  {t("nav.todayQueue")}
                </NavLink>
                <NavLink to="/doctor/schedule" className={navLinkClass}>
                  {t("nav.schedule")}
                </NavLink>
              </div>
            )}

            {user?.role === "admin" && (
              <div className="sidebar-group">
                <span className="sidebar-label">{t("roles.admin")}</span>
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
              </div>
            )}

            {user && (
              <div className="sidebar-group">
                <NavLink to="/profile" className={navLinkClass}>
                  {t("nav.profile")}
                </NavLink>
              </div>
            )}
          </nav>
        </aside>

        <main className="app-main">
          <AppRoutes />
        </main>
      </div>

      <footer className="app-footer">Shifokorxona CRM © 2026</footer>
    </div>
  );
}