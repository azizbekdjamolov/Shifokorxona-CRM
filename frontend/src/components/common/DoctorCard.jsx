import { useState } from "react";
import BookingModal from "./BookingModal";

export default function DoctorCard({ doctor }) {
  const [showBooking, setShowBooking] = useState(false);

  const fullName = doctor.user?.full_name || doctor.user?.email || "Shifokor";
  const photo = doctor.photo || null;

  return (
    <div className="doctor-card">
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
        Tajriba: {doctor.experience_years} yil • Narx: {doctor.price} so'm
      </p>
      <p className="doctor-rating">⭐ {doctor.average_rating || "—"}</p>
      <button className="btn btn-primary" onClick={() => setShowBooking(true)}>
        Band qilish
      </button>
      {showBooking && <BookingModal doctor={doctor} onClose={() => setShowBooking(false)} />}
    </div>
  );
}