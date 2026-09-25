import { useState } from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { requestPasswordReset, confirmPasswordReset } from "../../api/authApi";

export default function ForgotPasswordPage() {
  const { t } = useTranslation();
  const [step, setStep] = useState("request");
  const [email, setEmail] = useState("");
  const [code, setCode] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  const submitRequest = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setSuccess("");
    try {
      await requestPasswordReset(email);
      setStep("reset");
    } catch (err) {
      const data = err.response?.data;
      setError(data ? Object.values(data).flat()[0] : t("common.error"));
    } finally {
      setLoading(false);
    }
  };

  const submitReset = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setSuccess("");
    try {
      await confirmPasswordReset({ email, code, password, confirm_password: confirm });
      setSuccess(t("forgot.done"));
      setStep("done");
    } catch (err) {
      const data = err.response?.data;
      setError(data ? Object.values(data).flat()[0] : t("common.error"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-brand-panel">
        <div className="auth-brand-content">
          <Link to="/" className="auth-logo">
            Shifokorxona CRM
          </Link>
          <h1>{t("auth.tagline")}</h1>
          <p>{t("auth.taglineSub")}</p>
          <ul className="auth-features">
            <li>{t("auth.featBooking")}</li>
            <li>{t("auth.featQueue")}</li>
            <li>{t("auth.featPrescriptions")}</li>
            <li>{t("auth.featReviews")}</li>
          </ul>
        </div>
      </div>
      <div className="auth-form-panel">
        {step === "request" && (
          <form className="auth-form" onSubmit={submitRequest}>
            <h2>{t("forgot.title")}</h2>
            <p className="auth-subtitle">{t("forgot.subtitle")}</p>
            <label>
              {t("auth.email")}
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                required
                autoFocus
              />
            </label>
            {error && <p className="error-text">{error}</p>}
            <button className="btn btn-primary btn-block" disabled={loading}>
              {loading ? t("common.loading") : t("forgot.send")}
            </button>
            <p className="auth-switch">
              <Link to="/login" className="link-btn">
                ← {t("auth.login")}
              </Link>
            </p>
          </form>
        )}

        {step === "reset" && (
          <form className="auth-form" onSubmit={submitReset}>
            <h2>{t("forgot.resetTitle")}</h2>
            <p className="auth-subtitle">{t("forgot.codeHint")}</p>
            <label>
              {t("auth.code")}
              <input
                value={code}
                onChange={(e) => setCode(e.target.value)}
                placeholder="123456"
                maxLength={6}
                required
                autoFocus
              />
            </label>
            <label>
              {t("profile.newPassword")}
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                minLength={8}
                required
              />
            </label>
            <label>
              {t("profile.confirmNewPassword")}
              <input
                type="password"
                value={confirm}
                onChange={(e) => setConfirm(e.target.value)}
                minLength={8}
                required
              />
            </label>
            {error && <p className="error-text">{error}</p>}
            <button className="btn btn-primary btn-block" disabled={loading}>
              {loading ? t("common.loading") : t("forgot.resetBtn")}
            </button>
            <p className="auth-switch">
              <Link to="/login" className="link-btn">
                ← {t("auth.login")}
              </Link>
            </p>
          </form>
        )}

        {step === "done" && (
          <div className="auth-form">
            <h2>{t("forgot.successTitle")}</h2>
            {success && <p className="success-message">{success}</p>}
            <Link to="/login" className="btn btn-primary btn-block">
              {t("auth.loginBtn")}
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}