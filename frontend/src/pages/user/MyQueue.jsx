import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getMyBookings, cancelMyBooking } from "../../api/bookingsApi";

const statusText = {
  hold: "Vaqtinchalik band",
  confirmed: "Tasdiqlangan",
  completed: "Yakunlangan",
  cancelled: "Bekor qilingan",
};

export default function MyQueue() {
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    load();
  }, []);

  const load = () =>
    getMyBookings()
      .then((res) => setBookings(res.data.results || res.data))
      .finally(() => setLoading(false));

  const handleCancel = async (id) => {
    if (!window.confirm("Bronni bekor qilasizmi?")) return;
    await cancelMyBooking(id);
    load();
  };

  return (
    <div className="list-page">
      <h1>Mening navbatim</h1>
      {loading && <p>Yuklanmoqda...</p>}
      {!loading && bookings.length === 0 && (
        <p className="empty-state">Sizda bronlar yo'q.</p>
      )}
      <div className="card-list">
        {bookings.map((b) => (
          <div key={b.id} className="card booking-card">
            <div className="card-head">
              <h3>Dr. {b.doctor.user?.full_name}</h3>
              <span className={`status-badge status-${b.status}`}>
                {statusText[b.status]}
              </span>
            </div>
            <p>
              {b.date} • {b.time}
            </p>
            <p>{b.doctor.specialty_name}</p>
            {b.status === "hold" && b.hold_expires_at && (
              <p className="hint">⚠️ Hold: {b.hold_expires_at} gacha tasdiqlanishi kerak</p>
            )}
            {b.status === "completed" && !b.review && (
              <Link to={`/leave-review/${b.id}`} className="btn">
                Sharh qoldirish
              </Link>
            )}
            {(b.status === "hold" || b.status === "confirmed") && (
              <button className="btn btn-danger" onClick={() => handleCancel(b.id)}>
                Bekor qilish
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}