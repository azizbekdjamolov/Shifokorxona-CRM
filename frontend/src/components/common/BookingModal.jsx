import { useEffect, useState } from "react";
import { createPortal } from "react-dom";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useAuth } from "../../context/AuthContext";
import { createBooking } from "../../api/bookingsApi";
import { getDoctorAvailability } from "../../api/doctorsApi";

const DEFAULT_START = 7;
const DEFAULT_END = 21;

const rangeHours = (start, end) =>
  Array.from({ length: Math.max(0, end - start) }, (_, h) =>
    `${String(start + h).padStart(2, "0")}:00`
  );

const buildTimeSlots = (doctor, date) => {
  const schedule = doctor?.schedule || [];
  if (schedule.length === 0) {
    return rangeHours(DEFAULT_START, DEFAULT_END);
  }
  const pyWeekday = (new Date(date).getDay() + 6) % 7;
  const day = schedule.find((s) => s.weekday === pyWeekday);
  if (!day || !day.is_working) return [];
  const start = parseInt(day.start_time.slice(0, 2), 10);
  const end = parseInt(day.end_time.slice(0, 2), 10);
  return rangeHours(start, end);
};

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

const getPhoneDigits = (value) => {
  const digits = normalizePhone(value);
  return digits.startsWith("998") ? digits.slice(3) : digits;
};

const isValidPhone = (phoneDigits) => /^\d{9}$/.test(phoneDigits);

const formatDigits = (phoneDigits) => {
  const d = (phoneDigits || "").slice(0, 9);
  const parts = [d.slice(0, 2), d.slice(2, 5), d.slice(5, 7), d.slice(7, 9)].filter(
    Boolean
  );
  return parts.join(" ");
};

export default function BookingModal({ doctor, onClose, onSuccess }) {
  const { t } = useTranslation();
  const { user } = useAuth();
  const days = nextDays();

  const [firstName, setFirstName] = useState(user?.first_name || "");
  const [lastName, setLastName] = useState(user?.last_name || "");
  const [phoneDigits, setPhoneDigits] = useState(getPhoneDigits(user?.phone || ""));
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

  const [bookedTimes, setBookedTimes] = useState([]);

  useEffect(() => {
    if (!doctor?.id || !date) return;
    setBookedTimes([]);
    setTime("");
    getDoctorAvailability(doctor.id, { date })
      .then((res) => {
        setBookedTimes(res.data.booked_times || []);
      })
      .catch(() => setBookedTimes([]));
  }, [doctor?.id, date]);

  const timeSlots = buildTimeSlots(doctor, date);

  const isSlotBooked = (slot) => bookedTimes.includes(slot);

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
    if (!phoneDigits) errs.phone = t("booking.required");
    else if (!isValidPhone(phoneDigits)) errs.phone = t("booking.invalidPhone");
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
      const phone = `+998${phoneDigits}`;
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

  return createPortal(
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
                  <div className="phone-input">
                    <span className="phone-prefix">
                      <svg
                        viewBox="0 0 60 30"
                        className="phone-flag"
                        aria-hidden="true"
                      >
                        <rect width="60" height="30" fill="#1eb53a" />
                        <rect width="60" height="22.5" fill="white" />
                        <rect width="60" height="15" fill="#0099b5" />
                        <rect y="15" width="60" height="1" fill="#ce1126" />
                        <rect y="20.5" width="60" height="1" fill="#ce1126" />
                        <circle cx="9" cy="7" r="4.5" fill="white" />
                        <path d="M10.5 3.5 a4.5 4.5 0 0 1 0 7" fill="#0099b5" />
                        <circle cx="25" cy="3.5" r="1.1" fill="white" />
                        <circle cx="32" cy="3.5" r="1.1" fill="white" />
                        <circle cx="39" cy="3.5" r="1.1" fill="white" />
                        <circle cx="28.5" cy="7.5" r="1.1" fill="white" />
                        <circle cx="35.5" cy="7.5" r="1.1" fill="white" />
                        <circle cx="42.5" cy="7.5" r="1.1" fill="white" />
                        <circle cx="26" cy="11.5" r="1.1" fill="white" />
                        <circle cx="33" cy="11.5" r="1.1" fill="white" />
                        <circle cx="40" cy="11.5" r="1.1" fill="white" />
                        <circle cx="37.5" cy="15" r="1.1" fill="white" />
                        <circle cx="44.5" cy="15" r="1.1" fill="white" />
                      </svg>
                      +998
                    </span>
                    <input
                      type="tel"
                      inputMode="tel"
                      placeholder="90 123 45 67"
                      value={formatDigits(phoneDigits)}
                      onChange={(e) =>
                        setPhoneDigits(normalizePhone(e.target.value).slice(0, 9))
                      }
                    />
                  </div>
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
                      {timeSlots.map((start) => (
                        <option
                          key={start}
                          value={start}
                          disabled={isSlotBooked(start)}
                        >
                          {start} {isSlotBooked(start) ? "• band" : ""}
                        </option>
                      ))}
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
    </div>,
    document.body
  );
}