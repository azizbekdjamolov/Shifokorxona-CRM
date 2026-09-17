import { useEffect, useState } from "react";
import { getAdminBookings } from "../../api/bookingsApi";

const statusText = {
  hold: "Vaqtinchalik band",
  confirmed: "Tasdiqlangan",
  completed: "Yakunlangan",
  cancelled: "Bekor qilingan",
};

export default function ManageBookings() {
  const [bookings, setBookings] = useState([]);
  const [statusFilter, setStatusFilter] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    load();
  }, [statusFilter]);

  const load = () => {
    setLoading(true);
    getAdminBookings(
      statusFilter ? { status: statusFilter, page_size: 100 } : { page_size: 100 }
    )
      .then((res) => setBookings(res.data.results || res.data))
      .finally(() => setLoading(false));
  };

  return (
    <div className="list-page">
      <h1>Bronlar monitoringi</h1>
      <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
        <option value="">Barcha holatlar</option>
        {Object.entries(statusText).map(([key, name]) => (
          <option key={key} value={key}>
            {name}
          </option>
        ))}
      </select>
      {loading && <p>Yuklanmoqda...</p>}
      <div className="card-list">
        {bookings.map((b) => (
          <div key={b.id} className="card booking-card">
            <div className="card-head">
              <h3>
                {b.patient_name} → Dr. {b.doctor.user?.full_name}
              </h3>
              <span className={`status-badge status-${b.status}`}>
                {statusText[b.status]}
              </span>
            </div>
            <p>
              {b.date} • {b.time} • {b.doctor.specialty_name}
            </p>
          </div>
        ))}
      </div>
      {!loading && bookings.length === 0 && (
        <p className="empty-state">Bronlar topilmadi.</p>
      )}
    </div>
  );
}