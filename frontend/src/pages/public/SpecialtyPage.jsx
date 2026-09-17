import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { getDoctors, getSpecialties } from "../../api/doctorsApi";
import DoctorCard from "../../components/common/DoctorCard";

export default function SpecialtyPage() {
  const { slug } = useParams();
  const [specialty, setSpecialty] = useState(null);
  const [doctors, setDoctors] = useState([]);

  useEffect(() => {
    getSpecialties().then((res) => {
      const list = res.data.results || res.data;
      const found = list.find((s) => s.slug === slug);
      setSpecialty(found);
      if (found) {
        getDoctors({ specialty: found.id, page_size: 100 }).then((dr) =>
          setDoctors(dr.data.results || dr.data)
        );
      }
    });
  }, [slug]);

  return (
    <div className="specialty-page">
      <h1>{specialty ? specialty.name : "Yo'nalish"}</h1>
      <p>{specialty?.description}</p>
      <div className="doctors-grid">
        {doctors.map((d) => (
          <DoctorCard key={d.id} doctor={d} />
        ))}
      </div>
      {doctors.length === 0 && <p className="empty-state">Bu yo'nalishda shifokorlar yo'q</p>}
    </div>
  );
}