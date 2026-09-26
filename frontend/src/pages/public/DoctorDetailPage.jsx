import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useAuth } from "../../context/AuthContext";
import { getDoctor } from "../../api/doctorsApi";
import { getDoctorReviews } from "../../api/reviewsApi";
import BookingModal from "../../components/common/BookingModal";
import { openConversation } from "../../api/chatsApi";

const weekdayNames = ["D", "S", "Ch", "P", "J", "Sh", "Y"];

export default function DoctorDetailPage() {
  const { t } = useTranslation();
  const { id } = useParams();
  const { user } = useAuth();
  const [doctor, setDoctor] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [showBooking, setShowBooking] = useState(false);
  const [toast, setToast] = useState("");
  const [chatMsg, setChatMsg] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getDoctor(id)
      .then((res) => setDoctor(res.data))
      .catch(() => setDoctor(null))
      .finally(() => setLoading(false));
    getDoctorReviews(id)
      .then((res) => setReviews(res.data.results || res.data))
      .catch(() => setReviews([]));
  }, [id]);

  const startChat = async () => {
    if (!user) return;
    try {
      const res = await openConversation(Number(id));
      window.location.href = `/messages?chat=${res.data.id}`;
    } catch (err) {
      setChatMsg(err.response?.data?.detail || t("chat.error"));
    }
  };

  const handleBooked = () => {
    setShowBooking(false);
    setToast(t("booking.success"));
    window.setTimeout(() => setToast(""), 4000);
  };

  if (loading) return <p>{t("common.loading")}</p>;
  if (!doctor) return <p className="empty-state">{t("common.empty")}</p>;

  const fullName = doctor.user?.full_name || doctor.user?.email || "Shifokor";

  return (
    <div className="doctor-detail">
      <Link to="/doctors" className="link-btn">
        ← {t("nav.doctors")}
      </Link>
      {toast && <div className="toast toast-success">{toast}</div>}

      <div className="doctor-detail-head">
        <div className="doctor-card-photo doctor-detail-photo">
          {doctor.photo ? (
            <img src={doctor.photo} alt={fullName} />
          ) : (
            <div className="doctor-avatar">{fullName.charAt(0).toUpperCase()}</div>
          )}
        </div>
        <div className="doctor-detail-info">
          <h1>Dr. {fullName}</h1>
          <p className="doctor-specialty">{doctor.specialty_name}</p>
          <p>
            {t("doctor.experience")}: {doctor.experience_years} {t("doctor.years")} • {t("doctor.price")}:{" "}
            {Number(doctor.price || 0).toLocaleString("uz-UZ")} so'm
          </p>
          <p className="doctor-rating">⭐ {doctor.average_rating || "—"}</p>
          {doctor.bio && <p className="doctor-bio">{doctor.bio}</p>}
          <div className="card-actions">
            <button className="btn btn-primary" onClick={() => setShowBooking(true)}>
              {t("doctor.book")}
            </button>
            {user && (
              <button className="btn" onClick={startChat}>
                💬 {t("chat.start")}
              </button>
            )}
          </div>
          {chatMsg && <p className="error-text">{chatMsg}</p>}
        </div>
      </div>

      <div className="doctor-detail-sections">
        <section className="section-card">
          <h2>{t("nav.schedule")}</h2>
          <div className="schedule-grid">
            {(doctor.schedule || []).map((s) => (
              <div
                key={s.id}
                className={`schedule-day ${s.is_working ? "" : "schedule-day-off"}`}
              >
                <b>{weekdayNames[s.weekday]}</b>
                <span>
                  {s.is_working ? `${s.start_time.slice(0, 5)}-${s.end_time.slice(0, 5)}` : "—"}
                </span>
              </div>
            ))}
            {(doctor.schedule || []).length === 0 && (
              <p className="hint">{t("chat.noSchedule")}</p>
            )}
          </div>
        </section>

        <section className="section-card">
          <h2>
            📝 {t("review.title")} <span className="review-count">({reviews.length})</span>
          </h2>
          {reviews.length === 0 && <p className="empty-state">{t("review.none")}</p>}
          <div className="review-list">
            {reviews.map((r) => (
              <div key={r.id} className="review-item">
                <div className="review-head">
                  <b>{r.patient_name || "Bemor"}</b>
                  <span className="review-stars">{"⭐".repeat(r.rating)}</span>
                </div>
                {r.text && <p>{r.text}</p>}
                <span className="hint">{r.created_at?.slice(0, 10)}</span>
              </div>
            ))}
          </div>
        </section>
      </div>

      {showBooking && (
        <BookingModal
          doctor={doctor}
          onClose={() => setShowBooking(false)}
          onSuccess={handleBooked}
        />
      )}
    </div>
  );
}