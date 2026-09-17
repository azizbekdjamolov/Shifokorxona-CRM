import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { getDoctors, getSpecialties } from "../../api/doctorsApi";
import DoctorCard from "../../components/common/DoctorCard";

export default function DoctorsList() {
  const [searchParams] = useSearchParams();
  const [doctors, setDoctors] = useState([]);
  const [specialties, setSpecialties] = useState([]);
  const [search, setSearch] = useState("");
  const [specialty, setSpecialty] = useState(searchParams.get("specialty") || "");

  useEffect(() => {
    getSpecialties().then((res) => setSpecialties(res.data.results || res.data));
  }, []);

  useEffect(() => {
    const params = { page_size: 100 };
    if (search) params.search = search;
    if (specialty) params.specialty = specialty;
    getDoctors(params).then((res) => setDoctors(res.data.results || res.data));
  }, [search, specialty]);

  return (
    <div className="doctors-page">
      <div className="filter-bar">
        <input
          type="search"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Shifokor nomini qidirish..."
        />
        <select value={specialty} onChange={(e) => setSpecialty(e.target.value)}>
          <option value="">Barcha yo'nalishlar</option>
          {specialties.map((s) => (
            <option key={s.id} value={s.id}>
              {s.name}
            </option>
          ))}
        </select>
      </div>
      <div className="doctors-grid">
        {doctors.map((d) => (
          <DoctorCard key={d.id} doctor={d} />
        ))}
      </div>
      {doctors.length === 0 && <p className="empty-state">Shifokorlar topilmadi</p>}
    </div>
  );
}