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

  const printPrescription = (p) => {
    const days = ["Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma", "Shanba", "Yakshanba"];
    const html = `<!DOCTYPE html>
<html lang="uz"><head><meta charset="utf-8">
<title>Retsept — ${p.medicine_name}</title>
<style>
  body { font-family: Arial, sans-serif; color: #111; padding: 40px; }
  .head { display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid #2c6e49; padding-bottom: 12px; }
  .head h1 { font-size: 24px; margin: 0; color: #2c6e49; }
  .meta { color: #666; font-size: 13px; }
  .rx { border: 1px solid #ddd; border-left: 6px solid #2c6e49; padding: 24px; margin: 24px 0; border-radius: 6px; }
  .rx .name { font-size: 22px; font-weight: bold; }
  label { color: #888; font-size: 12px; text-transform: uppercase; letter-spacing: .5px; }
  .footer { margin-top: 40px; color: #888; font-size: 11px; text-align: center; border-top: 1px dashed #ddd; padding-top: 10px; }
</style></head>
<body>
  <div class="head">
    <div><h1>🩺 Shifokorxona CRM</h1><p class="meta">Elektron retsept</p></div>
    <div class="meta">Sana: ${p.created_at?.slice(0, 10)}</div>
  </div>
  <div class="rx">
    <label>Dori nomi</label>
    <div class="name">💊 ${p.medicine_name}</div>
    <p><label>Izoh:</label> ${p.instruction}</p>
    <p><label>Qabul:</label> Kuniga ${p.times_per_day} marta • ${p.days} kun</p>
    <p><label>Shifokor:</label> ${p.doctor_name}</p>
    ${p.image ? `<p><img src="${p.image}" style="max-width:280px;border:1px solid #ddd;border-radius:6px" /></p>` : ""}
  </div>
  <div class="footer">Shifokorxona CRM tomonidan yaratilgan elektron retsept</div>
  <script>window.onload = () => setTimeout(() => window.print(), 300);</script>
</body></html>`;
    const win = window.open("", "_blank");
    if (!win) return;
    win.document.open();
    win.document.write(html);
    win.document.close();
  };

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
            <div className="card-actions">
              <button className="btn" onClick={() => printPrescription(p)}>
                🖨️ {t("prescriptions.pdf")}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}