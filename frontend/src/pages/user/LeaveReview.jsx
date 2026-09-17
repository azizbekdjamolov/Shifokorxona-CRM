import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { createReview } from "../../api/reviewsApi";

export default function LeaveReview() {
  const { t } = useTranslation();
  const { bookingId } = useParams();
  const navigate = useNavigate();
  const [rating, setRating] = useState(5);
  const [text, setText] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const ratings = [1, 2, 3, 4, 5];

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      await createReview({ booking: Number(bookingId), rating, text });
      navigate("/my-queue");
    } catch (err) {
      setError(err.response?.data?.booking?.[0] || "Sharh yuborishda xatolik");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="form-page">
      <h1>{t("review.title")}</h1>
      <form className="auth-form" onSubmit={submit}>
        <label>
          {t("review.rating")}
          <div className="rating-picker">
            {ratings.map((r) => (
              <button
                key={r}
                type="button"
                className={r <= rating ? "star star-active" : "star"}
                onClick={() => setRating(r)}
              >
                ★
              </button>
            ))}
          </div>
        </label>
        <label>
          {t("review.text")}
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            rows={4}
            placeholder={t("review.placeholder")}
          />
        </label>
        {error && <p className="error-text">{error}</p>}
        <button className="btn btn-primary" disabled={loading}>
          {loading ? t("common.loading") : t("review.submit")}
        </button>
      </form>
    </div>
  );
}