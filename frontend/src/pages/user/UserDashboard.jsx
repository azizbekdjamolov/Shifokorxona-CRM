import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getMyBookings } from "../../api/bookingsApi";
import { getMyPrescriptions } from "../../api/prescriptionsApi";
import { useAuth } from "../../context/AuthContext";

export default function UserDashboard() {
  const { user } = useAuth();
  const [bookings, setBookings] = useState([]);
  const [prescriptions, setPrescriptions] = useState([]);

  useEffect(() => {
    getMyBookings().then((res) => setBookings(res.data.results || res.data));
    getMyPrescriptions().then((res) => setPrescriptions(res.data.results || res.data));
  }, []);

  const upcoming = bookings.filter((b) =>
    ["hold", "confirmed"].includes(b.status)
  );
  const completedCount = bookings.filter((b) => b.status === "completed").length;

  return (
    <div className="dashboard-page">
      <h1>Xush kelibsiz, {user?.first_name || user?.full_name}!</h1>

      <div className="stats-row">
        <div className="stat-card">
          <b>{upcoming.length}</b>
          <span>Yaqin bronlar</span>
        </div>
        <div className="stat-card">
          <b>{completedCount}</b>
          <span>Yakunlangan bronlar</span>
        </div>
        <div className="stat-card">
          <b>{prescriptions.length}</b>
          <span>Retseptlar</span>
        </div>
      </div>

      <div className="dashboard-links">
        <Link to="/my-queue" className="btn">
          Navbatim
        </Link>
        <Link to="/my-prescriptions" className="btn">
          Retseptlarim
        </Link>
        <Link to="/doctors" className="btn btn-primary">
          Yangi bron qilish
        </Link>
      </div>
    </div>
  );
}