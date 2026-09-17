import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { getMyPrescriptions } from "../../api/prescriptionsApi";

export default function MyPrescriptions() {
  const { t } = useTranslation();
  const [prescriptions, setPrescriptions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getMyPrescriptions()
      .then((res) => setPrescriptions(res.data.results || res.data))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="list-page">
      <h1>{t("prescriptions.title")}</h1>
      {loading && <p>{t("common.loading")}</p>}
      {!loading && prescriptions.length === 0 && (
        <p className="empty-state">{t("common.empty")}</p>
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
              {t("prescriptions.perDay")} {p.times_per_day} {t("prescriptions.times")} • {p.days}{" "}
              {t("prescriptions.forDays")}
            </p>
            <p>
              {t("prescriptions.doctor")}: {p.doctor_name}
            </p>
            {p.image && (
              <img src={p.image} alt={p.medicine_name} className="medicine-image" />
            )}
          </div>
        ))}
      </div>
    </div>
  );
}