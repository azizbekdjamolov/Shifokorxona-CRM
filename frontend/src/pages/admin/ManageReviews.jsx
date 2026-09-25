import { useEffect, useState } from "react";
import { getAdminReviews, moderateReview } from "../../api/reviewsApi";

const statusNames = {
  pending: "Kutilmoqda",
  approved: "Tasdiqlangan",
  rejected: "Rad etilgan",
};

export default function ManageReviews() {
  const [reviews, setReviews] = useState([]);
  const [statusFilter, setStatusFilter] = useState("pending");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    load();
  }, [statusFilter]);

  const load = () => {
    setLoading(true);
    getAdminReviews(statusFilter ? { status: statusFilter, page_size: 100 } : { page_size: 100 })
      .then((res) => setReviews(res.data.results || res.data))
      .finally(() => setLoading(false));
  };

  const moderate = async (id, status) => {
    await moderateReview(id, { status });
    load();
  };

  return (
    <div className="list-page">
      <h1>Sharhlar moderatsiyasi</h1>
      <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
        <option value="pending">Kutilmoqda</option>
        <option value="approved">Tasdiqlangan</option>
        <option value="rejected">Rad etilgan</option>
        <option value="">Barchasi</option>
      </select>
      {loading && <p>Yuklanmoqda...</p>}
      <div className="card-list">
        {reviews.map((r) => (
          <div key={r.id} className="card review-admin-card">
            <div className="card-head">
              <h3>
                {r.doctor_name || "Shifokor"} — {r.patient_name}
              </h3>
              <span className={`status-badge status-${r.status === "approved" ? "completed" : r.status === "rejected" ? "cancelled" : "hold"}`}>
                {statusNames[r.status]}
              </span>
            </div>
            <p className="review-stars">{"⭐".repeat(r.rating)}</p>
            {r.text && <p>{r.text}</p>}
            <span className="hint">{r.created_at?.slice(0, 10)}</span>
            {r.status === "pending" && (
              <div className="card-actions">
                <button className="btn btn-primary" onClick={() => moderate(r.id, "approved")}>
                  ✓ Tasdiqlash
                </button>
                <button className="btn btn-danger" onClick={() => moderate(r.id, "rejected")}>
                  ✕ Rad etish
                </button>
              </div>
            )}
          </div>
        ))}
      </div>
      {!loading && reviews.length === 0 && (
        <p className="empty-state">Bu holatda sharhlar yo'q.</p>
      )}
    </div>
  );
}