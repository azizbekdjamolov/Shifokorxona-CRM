import { Link, NavLink } from "react-router-dom";
import { useAuth } from "./context/AuthContext";
import ThemeToggle from "./components/ThemeToggle";
import LanguageSwitcher from "./components/LanguageSwitcher";
import PublicRoutes from "./routes/PublicRoutes";
import UserRoutes from "./routes/UserRoutes";
import DoctorRoutes from "./routes/DoctorRoutes";
import AdminRoutes from "./routes/AdminRoutes";

export default function App() {
  const { user, logout } = useAuth();

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
            Bosh sahifa
          </NavLink>
          <NavLink to="/doctors" className={navLinkClass}>
            Shifokorlar
          </NavLink>
          {user?.role === "patient" && (
            <>
              <NavLink to="/dashboard" className={navLinkClass}>
                Mening panel
              </NavLink>
              <NavLink to="/my-queue" className={navLinkClass}>
                Navbatim
              </NavLink>
              <NavLink to="/my-prescriptions" className={navLinkClass}>
                Retseptlarim
              </NavLink>
            </>
          )}
          {user?.role === "doctor" && (
            <>
              <NavLink to="/doctor" className={navLinkClass}>
                Shifokor paneli
              </NavLink>
              <NavLink to="/doctor/today-queue" className={navLinkClass}>
                Bugungi navbat
              </NavLink>
              <NavLink to="/doctor/schedule" className={navLinkClass}>
                Jadval
              </NavLink>
            </>
          )}
          {user?.role === "admin" && (
            <>
              <NavLink to="/admin" className={navLinkClass}>
                Admin panel
              </NavLink>
              <NavLink to="/admin/users" className={navLinkClass}>
                Userlar
              </NavLink>
              <NavLink to="/admin/doctors" className={navLinkClass}>
                Shifokorlar
              </NavLink>
              <NavLink to="/admin/bookings" className={navLinkClass}>
                Bronlar
              </NavLink>
            </>
          )}
        </nav>
        <div className="header-actions">
          <ThemeToggle />
          <LanguageSwitcher />
          {user ? (
            <div className="user-menu">
              <span>{user.full_name || user.email}</span>
              <button onClick={logout}>Chiqish</button>
            </div>
          ) : (
            <span className="guest-label">Kirilmagan</span>
          )}
        </div>
      </header>
      <main className="app-main">
        <PublicRoutes />
        <UserRoutes />
        <DoctorRoutes />
        <AdminRoutes />
      </main>
      <footer className="app-footer">Shifokorxona CRM © 2026</footer>
    </div>
  );
}