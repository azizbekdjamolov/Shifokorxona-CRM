import { useState } from "react";
import { Link, Navigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useAuth } from "../../context/AuthContext";
import OtpVerify from "./OtpVerify";

export default function RegisterPage() {
  const { t } = useTranslation();
  const { registerUser, isAuthenticated } = useAuth();
  const [step, setStep] = useState("register");
  const [pendingEmail, setPendingEmail] = useState("");
  const [form, setForm] = useState({
    first_name: "",
    last_name: "",
    phone: "",
    email: "",
    password: "",
    confirm_password: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  if (isAuthenticated) return <Navigate to="/" replace />;

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      await registerUser(form);
      setPendingEmail(form.email);
      setStep("otp");
    } catch (err) {
      const data = err.response?.data;
      const firstError = data ? Object.values(data).flat()[0] : null;
      setError(firstError || t("auth.wrongCredentials"));
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
        {step === "otp" ? (
          <OtpVerify email={pendingEmail} onSuccess={() => {}} />
        ) : (
          <form className="auth-form" onSubmit={submit}>
            <h2>{t("auth.registerTitle")}</h2>
            <p className="auth-subtitle">{t("auth.registerSubtitle")}</p>
            <div className="auth-row">
              <label>
                {t("auth.firstName")}
                <input name="first_name" value={form.first_name} onChange={handleChange} required />
              </label>
              <label>
                {t("auth.lastName")}
                <input name="last_name" value={form.last_name} onChange={handleChange} required />
              </label>
            </div>
            <label>
              {t("auth.phone")}
              <input name="phone" value={form.phone} onChange={handleChange} placeholder="+998..." />
            </label>
            <label>
              {t("auth.email")}
              <input type="email" name="email" value={form.email} onChange={handleChange} required />
            </label>
            <label>
              {t("auth.password")}
              <input
                type="password"
                name="password"
                value={form.password}
                onChange={handleChange}
                minLength={8}
                required
              />
            </label>
            <label>
              {t("auth.confirmPassword")}
              <input
                type="password"
                name="confirm_password"
                value={form.confirm_password}
                onChange={handleChange}
                minLength={8}
                required
              />
            </label>
            {error && <p className="error-text">{error}</p>}
            <button className="btn btn-primary btn-block" disabled={loading}>
              {loading ? t("common.loading") : t("auth.registerBtn")}
            </button>
            <p className="auth-switch">
              {t("auth.hasAccount")}{" "}
              <Link to="/login" className="link-btn">
                {t("auth.login")}
              </Link>
            </p>
            <Link to="/" className="auth-back">
              ← {t("auth.backHome")}
            </Link>
          </form>
        )}
      </div>
    </div>
  );
}