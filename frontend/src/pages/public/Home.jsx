import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getSpecialties, getDoctors } from "../../api/doctorsApi";
import DoctorCard from "../../components/common/DoctorCard";

export default function Home() {
  const [specialties, setSpecialties] = useState([]);
  const [doctors, setDoctors] = useState([]);

  useEffect(() => {
    getSpecialties().then((res) => setSpecialties(res.data.results || res.data));
    getDoctors({ page_size: 6 }).then((res) => setDoctors(res.data.results || res.data));
  }, []);

  return (
    <div className="home-page">
      <section className="hero">
        <h1>Shifokorxona CRM ga xush kelibsiz</h1>
        <p>Shifokorlarga onlayn yoziling, navbatingizni kuzating, retseptlaringizni ko'ring.</p>
        <Link to="/doctors" className="btn btn-primary">
          Shifokorlarni ko'rish
        </Link>
      </section>

      <section className="section">
        <h2>Yo'nalishlar</h2>
        <div className="specialty-grid">
          {specialties.map((s) => (
            <Link key={s.id} to={`/specialties/${s.slug}`} className="specialty-card">
              <span className="specialty-icon">{s.icon || "🏥"}</span>
              <span>{s.name}</span>
            </Link>
          ))}
        </div>
      </section>

      <section className="section">
        <h2>Mashhur shifokorlar</h2>
        <div className="doctors-grid">
          {doctors.map((d) => (
            <DoctorCard key={d.id} doctor={d} />
          ))}
        </div>
      </section>
    </div>
  );
}