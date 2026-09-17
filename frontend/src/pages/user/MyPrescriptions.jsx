import { useEffect, useState } from "react";
import { getMyPrescriptions } from "../../api/prescriptionsApi";

export default function MyPrescriptions() {
  const [prescriptions, setPrescriptions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getMyPrescriptions()
      .then((res) => setPrescriptions(res.data.results || res.data))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="list-page">
      <h1>Mening retseptlarim</h1>
      {loading && <p>Yuklanmoqda...</p>}
      {!loading && prescriptions.length === 0 && (
        <p className="empty-state">Sizda retseptlar yo'q.</p>
      )}
      <div className="card-list">
        {prescriptions.map((p) => (
          <div key={p.id} className="card prescription-card">
            <div className="card-head">
              <h3>💊 {p.medicine_name}</h3>
              <span className="hint">{p.created_at?.slice(0, 10)}</span>
            </div>
            <p>{p.instruction}</p>
            <p>
              Kuniga {p.times_per_day} marta • {p.days} kun
            </p>
            <p>Shifokor: {p.doctor_name}</p>
            {p.image && (
              <img src={p.image} alt={p.medicine_name} className="medicine-image" />
            )}
          </div>
        ))}
      </div>
    </div>
  );
}