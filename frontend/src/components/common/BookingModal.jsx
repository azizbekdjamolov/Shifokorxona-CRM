import { useState } from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useAuth } from "../../context/AuthContext";
import { createBooking } from "../../api/bookingsApi";

const nextDays = () => {
  const days = [];
  const now = new Date();
  for (let i = 0; i < 7; i++) {
    const d = new Date(now);
    d.setDate(now.getDate() + i);
    days.push(d.toISOString().slice(0, 10));
  }
  return days;
};

export default function BookingModal({ doctor, onClose }) {
  const { t } = useTranslation();
  const { user } = useAuth();
  const [date, setDate] = useState(nextDays()[0]);
  const [time, setTime] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  const schedule = doctor.schedule || [];
  const todaySlots = schedule.filter((s) => {
    const weekDay = new Date(date).getDay();
    return s.weekday === weekDay;
  });

  const submit = async () => {
    setLoading(true);
    setError("");
    try {
      await createBooking({ doctor: doctor.id, date, time });
      setSuccess(true);
    } catch (err) {
      setError(err.response?.data?.time?.[0] || err.response?.data?.detail || t("booking.error"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>
          ✕
        </button>
        <h2>
          Dr. {doctor.user?.full_name} {t("booking.title")}
        </h2>

        {!user && (
          <div className="booking-login-prompt">
            <p>{t("booking.needLogin")}</p>
            <Link to="/login" className="btn btn-primary">
              {t("auth.login")}
            </Link>
            <Link to="/register" className="link-btn">
              {t("auth.register")}
            </Link>
          </div>
        )}

        {user && (
          <div className="booking-form">
            {success ? (
              <div className="success-message">
                <p>✅ {t("booking.success")}</p>
                <button className="btn" onClick={onClose}>
                  {t("booking.close")}
                </button>
              </div>
            ) : (
              <>
                <label>
                  {t("booking.date")}
                  <select value={date} onChange={(e) => setDate(e.target.value)}>
                    {nextDays().map((d) => (
                      <option key={d} value={d}>
                        {d}
                      </option>
                    ))}
                  </select>
                </label>
                <label>
                  {t("booking.time")}
                  <select value={time} onChange={(e) => setTime(e.target.value)}>
                    <option value="">{t("booking.selectTime")}</option>
                    {todaySlots.map((slot) => {
                      const start = slot.start_time.slice(0, 5);
                      return (
                        <option key={slot.id} value={start}>
                          {start}
                        </option>
                      );
                    })}
                  </select>
                </label>
                {error && <p className="error-text">{error}</p>}
                <button className="btn btn-primary" onClick={submit} disabled={!time || loading}>
                  {loading ? t("common.loading") : t("booking.confirm")}
                </button>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}