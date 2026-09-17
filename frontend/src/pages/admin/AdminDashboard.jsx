import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getAdminUsers } from "../../api/authApi";
import { getAdminDoctors } from "../../api/doctorsApi";
import { getAdminBookings } from "../../api/bookingsApi";

export default function AdminDashboard() {
  const [users, setUsers] = useState([]);
  const [doctors, setDoctors] = useState([]);
  const [bookings, setBookings] = useState([]);

  useEffect(() => {
    getAdminUsers({ page_size: 100 }).then((res) => setUsers(res.data.results || res.data));
    getAdminDoctors({ page_size: 100 }).then((res) => setDoctors(res.data.results || res.data));
    getAdminBookings({ page_size: 100 }).then((res) => setBookings(res.data.results || res.data));
  }, []);

  const statusCount = (s) => bookings.filter((b) => b.status === s).length;

  return (
    <div className="dashboard-page">
      <h1>Admin panel</h1>
      <div className="stats-row">
        <div className="stat-card">
          <b>{users.length}</b>
          <span>Foydalanuvchilar</span>
        </div>
        <div className="stat-card">
          <b>{doctors.length}</b>
          <span>Shifokorlar</span>
        </div>
        <div className="stat-card">
          <b>{bookings.length}</b>
          <span>Bronlar</span>
        </div>
      </div>
      <div className="stats-row">
        <div className="stat-card">
          <b>{statusCount("hold")}</b>
          <span>Hold</span>
        </div>
        <div className="stat-card">
          <b>{statusCount("confirmed")}</b>
          <span>Tasdiqlangan</span>
        </div>
        <div className="stat-card">
          <b>{statusCount("completed")}</b>
          <span>Yakunlangan</span>
        </div>
      </div>
      <div className="dashboard-links">
        <Link to="/admin/users" className="btn">
          Userlar
        </Link>
        <Link to="/admin/doctors" className="btn">
          Shifokorlar
        </Link>
        <Link to="/admin/specialties" className="btn">
          Yo'nalishlar
        </Link>
        <Link to="/admin/bookings" className="btn btn-primary">
          Bronlar
        </Link>
      </div>
    </div>
  );
}