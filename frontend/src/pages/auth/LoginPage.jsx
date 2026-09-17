import { useState } from "react";
import { Link, Navigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useAuth } from "../../context/AuthContext";

export default function LoginPage() {
  const { t } = useTranslation();
  const { login, isAuthenticated } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  if (isAuthenticated) return <Navigate to="/" replace />;

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      await login(email, password);
    } catch {
      setError(t("auth.wrongCredentials"));
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
        <form className="auth-form" onSubmit={submit}>
          <h2>{t("auth.welcomeBack")}</h2>
          <p className="auth-subtitle">{t("auth.loginSubtitle")}</p>
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
          <label>
            {t("auth.password")}
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
            />
          </label>
          {error && <p className="error-text">{error}</p>}
          <button className="btn btn-primary btn-block" disabled={loading}>
            {loading ? t("common.loading") : t("auth.loginBtn")}
          </button>
          <p className="auth-switch">
            {t("auth.noAccount")}{" "}
            <Link to="/register" className="link-btn">
              {t("auth.register")}
            </Link>
          </p>
          <Link to="/" className="auth-back">
            ← {t("auth.backHome")}
          </Link>
        </form>
      </div>
    </div>
  );
}