import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getDoctorTodayQueue } from "../../api/bookingsApi";
import { getDoctorMe, updateDoctorMe } from "../../api/doctorsApi";
import { useAuth } from "../../context/AuthContext";

export default function DoctorDashboard() {
  const { user } = useAuth();
  const [profile, setProfile] = useState(null);
  const [today, setToday] = useState([]);
  const [photo, setPhoto] = useState(null);
  const [photoMsg, setPhotoMsg] = useState("");

  useEffect(() => {
    getDoctorMe().then((res) => setProfile(res.data));
    getDoctorTodayQueue().then((res) => setToday(res.data.results || res.data));
  }, []);

  const uploadPhoto = async () => {
    if (!photo) return;
    setPhotoMsg("");
    const data = new FormData();
    data.append("photo", photo);
    try {
      const res = await updateDoctorMe(data);
      setProfile(res.data);
      setPhoto(null);
      setPhotoMsg("✅ Foto yangilandi");
    } catch (err) {
      setPhotoMsg(err.response?.data?.photo?.[0] || "Xatolik");
    }
  };

  const waitCount = today.filter((b) => b.status === "confirmed").length;
  const doneCount = today.filter((b) => b.status === "completed").length;

  return (
    <div className="dashboard-page">
      <h1>Dr. {user?.full_name}</h1>
      {profile && (
        <p>
          {profile.specialty_name} • Tajriba: {profile.experience_years} yil • ⭐{" "}
          {profile.average_rating}
        </p>
      )}

      <div className="stats-row">
        <div className="stat-card">
          <b>{today.length}</b>
          <span>Bugungi navbat</span>
        </div>
        <div className="stat-card">
          <b>{waitCount}</b>
          <span>Kutilayotgan</span>
        </div>
        <div className="stat-card">
          <b>{doneCount}</b>
          <span>Yakunlangan</span>
        </div>
      </div>

      <div className="dashboard-links">
        <Link to="/doctor/today-queue" className="btn btn-primary">
          Bugungi navbat
        </Link>
        <Link to="/doctor/add-prescription" className="btn">
          Retsept yozish
        </Link>
        <Link to="/doctor/schedule" className="btn">
          Ish jadvali
        </Link>
        <Link to="/messages" className="btn">
          💬 Xabarlar
        </Link>
      </div>

      <div className="dashboard-photo-box">
        <h3>Foto yangilash</h3>
        {profile?.photo && <img src={profile.photo} alt="profil" className="doctor-avatar-img" />}
        <input type="file" accept="image/*" onChange={(e) => setPhoto(e.target.files[0])} />
        <button className="btn btn-primary" onClick={uploadPhoto} disabled={!photo}>
          Foto yuklash
        </button>
        {photoMsg && <p className={photoMsg.startsWith("✅") ? "success-message" : "error-text"}>{photoMsg}</p>}
      </div>
    </div>
  );
}