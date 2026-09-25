import { useState } from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import BookingModal from "./BookingModal";

export default function DoctorCard({ doctor }) {
  const { t } = useTranslation();
  const [showBooking, setShowBooking] = useState(false);

  const fullName = doctor.user?.full_name || doctor.user?.email || "Shifokor";
  const photo = doctor.photo || null;

  return (
    <div className="doctor-card">
      <Link to={`/doctors/${doctor.id}`} className="doctor-card-link">
        <div className="doctor-card-photo">
          {photo ? (
            <img src={photo} alt={fullName} />
          ) : (
            <div className="doctor-avatar">🩺</div>
          )}
        </div>
        <h3>Dr. {fullName}</h3>
        <p className="doctor-specialty">{doctor.specialty_name}</p>
        <p>
          {t("doctor.experience")}: {doctor.experience_years} {t("doctor.years")} • {t("doctor.price")}: {doctor.price}
        </p>
        <p className="doctor-rating">
          ⭐ {doctor.average_rating || "—"}
        </p>
      </Link>
      <button className="btn btn-primary" onClick={() => setShowBooking(true)}>
        {t("doctor.book")}
      </button>
      {showBooking && <BookingModal doctor={doctor} onClose={() => setShowBooking(false)} />}
    </div>
  );
}