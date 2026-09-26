import { useState } from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import BookingModal from "./BookingModal";

export default function DoctorCard({ doctor }) {
  const { t } = useTranslation();
  const [showBooking, setShowBooking] = useState(false);
  const [toast, setToast] = useState("");

  const fullName = doctor.user?.full_name || doctor.user?.email || "Shifokor";
  const photo = doctor.photo || null;

  const handleBooked = () => {
    setShowBooking(false);
    setToast(t("booking.success"));
    window.setTimeout(() => setToast(""), 4000);
  };

  return (
    <div className="doctor-card">
      {toast && <div className="toast toast-success">{toast}</div>}
      <Link to={`/doctors/${doctor.id}`} className="doctor-card-link">
        <div className="doctor-card-photo">
          {photo ? (
            <img src={photo} alt={fullName} loading="lazy" />
          ) : (
            <div className="doctor-avatar">{fullName.charAt(0).toUpperCase()}</div>
          )}
        </div>
        <h3 className="doctor-name">Dr. {fullName}</h3>
        <p className="doctor-specialty">{doctor.specialty_name}</p>
        <p className="doctor-meta">
          {t("doctor.experience")}: {doctor.experience_years} {t("doctor.years")}
        </p>
        <p className="doctor-price">
          {t("doctor.price")}: {Number(doctor.price || 0).toLocaleString("uz-UZ")} so'm
        </p>
        <p className="doctor-rating">⭐ {doctor.average_rating || "—"}</p>
      </Link>
      <button className="btn btn-primary doctor-book-btn" onClick={() => setShowBooking(true)}>
        {t("doctor.book")}
      </button>
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