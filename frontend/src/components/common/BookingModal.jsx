import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useAuth } from "../../context/AuthContext";
import { createBooking } from "../../api/bookingsApi";

const nextDays = () => {
  const days = [];
  const now = new Date();
  for (let i = 0; i < 14; i++) {
    const d = new Date(now);
    d.setDate(now.getDate() + i);
    days.push(d.toISOString().slice(0, 10));
  }
  return days;
};

const normalizePhone = (value) => (value || "").replace(/\D/g, "");

const isValidPhone = (value) => {
  const digits = normalizePhone(value);
  return /^998\d{9}$/.test(digits);
};

const formatPhone = (value) => {
  const digits = normalizePhone(value).slice(0, 12);
  if (!digits.startsWith("998")) return digits;
  const rest = digits.slice(3);
  const parts = [
    "+",
    digits.slice(0, 3),
    rest.slice(0, 2),
    rest.slice(2, 5),
    rest.slice(5, 7),
    rest.slice(7, 9),
  ].filter(Boolean);
  return parts.join(" ");
};

export default function BookingModal({ doctor, onClose, onSuccess }) {
  const { t } = useTranslation();
  const { user } = useAuth();
  const days = nextDays();

  const [firstName, setFirstName] = useState(user?.first_name || "");
  const [lastName, setLastName] = useState(user?.last_name || "");
  const [phone, setPhone] = useState(user?.phone || "");
  const [date, setDate] = useState(days[0]);
  const [time, setTime] = useState("");
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    const onKey = (e) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", onKey);
    const prevOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.removeEventListener("keydown", onKey);
      document.body.style.overflow = prevOverflow;
    };
  }, [onClose]);

  const schedule = doctor.schedule || [];
  const todaySlots = schedule.filter((s) => {
    const weekDay = new Date(date).getDay();
    return s.weekday === weekDay;
  });

  const selectedDate = new Date(date);
  const weekdayLabel = selectedDate.toLocaleDateString(user?.role ? "uz-UZ" : "uz-UZ", {
    weekday: "long",
    day: "numeric",
    month: "long",
  });

  const validate = () => {
    const errs = {};
    if (!firstName.trim()) errs.firstName = t("booking.required");
    if (!lastName.trim()) errs.lastName = t("booking.required");
    if (!phone.trim()) errs.phone = t("booking.required");
    else if (!isValidPhone(phone)) errs.phone = t("booking.invalidPhone");
    if (!date) errs.date = t("booking.required");
    if (!time) errs.time = t("booking.required");
    return errs;
  };

  const submit = async () => {
    const errs = validate();
    setErrors(errs);
    if (Object.keys(errs).length > 0) return;
    setLoading(true);
    setError("");
    try {
      await createBooking({
        doctor: doctor.id,
        date,
        time,
        first_name: firstName,
        last_name: lastName,
        phone,
      });
      if (onSuccess) {
        onSuccess();
        return;
      }
      setSuccess(true);
    } catch (err) {
      setError(
        err.response?.data?.time?.[0] ||
          err.response?.data?.detail ||
          err.response?.data?.date?.[0] ||
          t("booking.error")
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal booking-modal" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose} aria-label={t("common.close")}>
          ✕
        </button>

        {!user ? (
          <div className="booking-login-prompt">
            <h2>{t("booking.title")}</h2>
            <p>{t("booking.needLogin")}</p>
            <Link to="/login" className="btn btn-primary">
              {t("auth.login")}
            </Link>
            <Link to="/register" className="link-btn">
              {t("auth.register")}
            </Link>
          </div>
        ) : (
          <div className="booking-form">
            <h2>{t("booking.modalTitle")}</h2>
            <p className="modal-subtitle">{t("booking.subtitle")}</p>

            <div className="booking-doctor">
              <div className="booking-doctor-photo">
                {doctor.photo ? (
                  <img src={doctor.photo} alt={doctor.user?.full_name} />
                ) : (
                  <span className="booking-doctor-avatar">
                    {(doctor.user?.full_name || "D").charAt(0).toUpperCase()}
                  </span>
                )}
              </div>
              <div className="booking-doctor-info">
                <p className="booking-doctor-name">Dr. {doctor.user?.full_name}</p>
                <p className="booking-doctor-specialty">{doctor.specialty_name}</p>
                <p className="booking-doctor-meta">
                  {t("doctor.experience")}: {doctor.experience_years} {t("doctor.years")} •{" "}
                  {t("doctor.price")}: {Number(doctor.price || 0).toLocaleString("uz-UZ")} so'm
                </p>
              </div>
            </div>

            {success ? (
              <div className="success-message">
                <p className="success-title">✅ {t("booking.success")}</p>
                <button className="btn btn-primary" onClick={onClose}>
                  {t("booking.close")}
                </button>
              </div>
            ) : (
              <div className="booking-fields">
                <div className="form-row">
                  <label>
                    {t("auth.firstName")}
                    <input
                      type="text"
                      value={firstName}
                      onChange={(e) => setFirstName(e.target.value)}
                    />
                    {errors.firstName && <span className="field-error">{errors.firstName}</span>}
                  </label>
                  <label>
                    {t("auth.lastName")}
                    <input
                      type="text"
                      value={lastName}
                      onChange={(e) => setLastName(e.target.value)}
                    />
                    {errors.lastName && <span className="field-error">{errors.lastName}</span>}
                  </label>
                </div>
                <label>
                  {t("auth.phone")}
                  <input
                    type="tel"
                    inputMode="tel"
                    placeholder="+998 90 123 45 67"
                    value={phone}
                    onChange={(e) => setPhone(formatPhone(e.target.value))}
                  />
                  {errors.phone && <span className="field-error">{errors.phone}</span>}
                </label>
                <div className="form-row">
                  <label>
                    {t("booking.date")}
                    <input
                      type="date"
                      min={days[0]}
                      value={date}
                      onChange={(e) => {
                        setDate(e.target.value);
                        setTime("");
                      }}
                    />
                    {errors.date && <span className="field-error">{errors.date}</span>}
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
                    {errors.time && <span className="field-error">{errors.time}</span>}
                  </label>
                </div>
                <p className="booking-date-hint">
                  {weekdayLabel} — {date}
                </p>
                {error && <p className="error-text">{error}</p>}
                <div className="booking-actions">
                  <button className="btn btn-outline" onClick={onClose} disabled={loading}>
                    {t("common.cancel")}
                  </button>
                  <button className="btn btn-primary" onClick={submit} disabled={loading}>
                    {loading ? t("common.loading") : t("doctor.book")}
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}