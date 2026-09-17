import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { getSpecialties, getDoctors } from "../../api/doctorsApi";
import DoctorCard from "../../components/common/DoctorCard";

export default function Home() {
  const { t } = useTranslation();
  const [specialties, setSpecialties] = useState([]);
  const [doctors, setDoctors] = useState([]);

  useEffect(() => {
    getSpecialties().then((res) => setSpecialties(res.data.results || res.data));
    getDoctors({ page_size: 6 }).then((res) => setDoctors(res.data.results || res.data));
  }, []);

  return (
    <div className="home-page">
      <section className="hero">
        <h1>{t("home.heroTitle")}</h1>
        <p>{t("home.heroText")}</p>
        <Link to="/doctors" className="btn btn-primary">
          {t("home.ctaDoctors")}
        </Link>
      </section>

      <section className="section">
        <h2>{t("home.specialties")}</h2>
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
        <h2>{t("home.popularDoctors")}</h2>
        <div className="doctors-grid">
          {doctors.map((d) => (
            <DoctorCard key={d.id} doctor={d} />
          ))}
        </div>
      </section>
    </div>
  );
}