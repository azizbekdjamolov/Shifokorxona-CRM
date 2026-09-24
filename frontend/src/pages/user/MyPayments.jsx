import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { getMyPayments, cancelPayment } from "../../api/paymentsApi";

export default function MyPayments() {
  const { t } = useTranslation();
  const [payments, setPayments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getMyPayments()
      .then((res) => setPayments(res.data.results || res.data))
      .finally(() => setLoading(false));
  }, []);

  const handleCancel = async (id) => {
    if (!window.confirm(t("payments.cancelPayment"))) return;
    await cancelPayment(id);
    const { data } = await getMyPayments();
    setPayments(data.results || data);
  };

  return (
    <div className="list-page">
      <h1>{t("nav.myPayments")}</h1>
      {loading && <p>{t("common.loading")}</p>}
      {!loading && payments.length === 0 && (
        <p className="empty-state">{t("payments.noPayments")}</p>
      )}
      <div className="card-list">
        {payments.map((p) => (
          <div key={p.id} className="card booking-card">
            <div className="card-head">
              <h3>{t("payments.doctor")}: Dr. {p.booking?.doctor?.user?.full_name || "-"}</h3>
              <span className={`status-badge status-${p.status}`}>
                {t(`payments.${p.status}`)}
              </span>
            </div>
            <p>
              {t("payments.amount")}: {p.amount} so'm
            </p>
            <p>
              {t("payments.provider")}: {p.provider_display || p.provider}
            </p>
            <p>
              {t("payments.date")}: {p.created_at?.slice(0, 10)}
            </p>
            {p.status === "pending" && (
              <button className="btn btn-danger" onClick={() => handleCancel(p.id)}>
                {t("payments.cancelPayment")}
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}