import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getDoctorTodayQueue, updateBookingStatus } from "../../api/bookingsApi";

const statusText = {
  hold: "Vaqtinchalik band",
  confirmed: "Tasdiqlangan",
  completed: "Yakunlangan",
  cancelled: "Bekor qilingan",
};

export default function TodayQueue() {
  const navigate = useNavigate();
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    load();
  }, []);

  const load = () =>
    getDoctorTodayQueue()
      .then((res) => setBookings(res.data.results || res.data))
      .finally(() => setLoading(false));

  const changeStatus = async (id, status) => {
    await updateBookingStatus(id, { status });
    load();
  };

  return (
    <div className="list-page">
      <h1>Bugungi navbat</h1>
      {loading && <p>Yuklanmoqda...</p>}
      {!loading && bookings.length === 0 && (
        <p className="empty-state">Bugunga bronlar yo'q.</p>
      )}
      <div className="card-list">
        {bookings.map((b, i) => (
          <div key={b.id} className="card booking-card">
            <div className="card-head">
              <h3>
                {i + 1}. {b.patient_name}
              </h3>
              <span className={`status-badge status-${b.status}`}>
                {statusText[b.status]}
              </span>
            </div>
            <p>
              {b.date} • {b.time}
            </p>
            <div className="card-actions">
              {b.status === "hold" && (
                <button className="btn btn-primary" onClick={() => changeStatus(b.id, "confirmed")}>
                  Tasdiqlash
                </button>
              )}
              {b.status === "confirmed" && (
                <>
                  <button className="btn btn-primary" onClick={() => changeStatus(b.id, "completed")}>
                    Yakunlash
                  </button>
                  <button className="btn btn-danger" onClick={() => changeStatus(b.id, "cancelled")}>
                    Bekor qilish
                  </button>
                </>
              )}
              {b.status === "completed" && (
                <button
                  className="btn"
                  onClick={() =>
                    navigate(`/doctor/add-prescription?booking=${b.id}&patient=${b.patient_name}`)
                  }
                >
                  💊 Retsept yozish
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}