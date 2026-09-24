import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { getMyBookings, cancelMyBooking } from "../../api/bookingsApi";
import { getPaymentProviders, initiatePayment, mockPay, cancelPayment } from "../../api/paymentsApi";

const statusText = {
  hold: "Vaqtinchalik band",
  confirmed: "Tasdiqlangan",
  completed: "Yakunlangan",
  cancelled: "Bekor qilingan",
};

const paymentText = {
  pending: "Kutilmoqda",
  paid: "To'langan",
  cancelled: "Bekor qilingan",
  failed: "Muvaffaqiyatsiz",
};

export default function MyQueue() {
  const { t } = useTranslation();
  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [providers, setProviders] = useState([]);
  const [busy, setBusy] = useState({});

  useEffect(() => {
    load();
    getPaymentProviders()
      .then((res) => setProviders(res.data.providers || []))
      .catch(() => {});
  }, []);

  const load = () =>
    getMyBookings()
      .then((res) => setBookings(res.data.results || res.data))
      .finally(() => setLoading(false));

  const handleCancel = async (id) => {
    if (!window.confirm(t("common.confirmQuestion"))) return;
    await cancelMyBooking(id);
    load();
  };

  const handlePay = async (booking) => {
    setBusy((s) => ({ ...s, [booking.id]: "init" }));
    try {
      const { data } = await initiatePayment(booking.id, providers[0]?.key || "mock");
      await mockPay(data.id);
      load();
    } catch {
      alert(t("common.error"));
    } finally {
      setBusy((s) => ({ ...s, [booking.id]: undefined }));
    }
  };

  const handleCancelPayment = async (payment) => {
    if (!window.confirm(t("payments.cancelPayment"))) return;
    await cancelPayment(payment.id);
    load();
  };

  return (
    <div className="list-page">
      <h1>{t("queue.title")}</h1>
      {loading && <p>{t("common.loading")}</p>}
      {!loading && bookings.length === 0 && (
        <p className="empty-state">{t("common.empty")}</p>
      )}
      <div className="card-list">
        {bookings.map((b) => (
          <div key={b.id} className="card booking-card">
            <div className="card-head">
              <h3>Dr. {b.doctor.user?.full_name}</h3>
              <span className={`status-badge status-${b.status}`}>
                {statusText[b.status]}
              </span>
            </div>
            <p>
              {b.date} • {b.time}
            </p>
            <p>{b.doctor.specialty_name}</p>
            {b.status === "hold" && b.hold_expires_at && (
              <p className="hint">⚠️ {b.hold_expires_at} {t("queue.holdWarning")}</p>
            )}
            {b.status === "completed" && !b.review && (
              <Link to={`/leave-review/${b.id}`} className="btn">
                {t("queue.leaveReview")}
              </Link>
            )}
            {b.status === "confirmed" && (
              <>
                <p className="hint">
                  {t("doctor.price")}: {b.doctor.price} so'm
                </p>
                {!b.payments || b.payments.status === "cancelled" || b.payments.status === "failed" ? (
                  <button
                    className="btn btn-primary"
                    disabled={!!busy[b.id]}
                    onClick={() => handlePay(b)}
                  >
                    {busy[b.id] ? t("common.loading") : t("queue.pay")}
                  </button>
                ) : (
                  <p className={`status-badge status-${b.payments.status}`}>
                    {t(`payments.${b.payments.status}`)} ({b.payments.provider})
                  </p>
                )}
              </>
            )}
            {(b.status === "hold" || b.status === "confirmed") && (
              <button className="btn btn-danger" onClick={() => handleCancel(b.id)}>
                {t("queue.cancel")}
              </button>
            )}
            {b.payments?.status === "pending" && (
              <button className="btn btn-outline" onClick={() => handleCancelPayment(b.payments)}>
                {t("payments.cancelPayment")}
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}