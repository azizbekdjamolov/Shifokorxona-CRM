import { useState } from "react";
import { useTranslation } from "react-i18next";
import { useAuth } from "../../context/AuthContext";

export default function RegisterForm({ onOtpRequired, onBack }) {
  const { t } = useTranslation();
  const { registerUser } = useAuth();
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

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      await registerUser(form);
      if (onOtpRequired) onOtpRequired(form.email);
    } catch (err) {
      const data = err.response?.data;
      const firstError = data ? Object.values(data).flat()[0] : null;
      setError(firstError || t("auth.wrongCredentials"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <form className="auth-form" onSubmit={submit}>
      <h2>{t("auth.registerTitle")}</h2>
      <label>
        {t("auth.firstName")}
        <input name="first_name" value={form.first_name} onChange={handleChange} required />
      </label>
      <label>
        {t("auth.lastName")}
        <input name="last_name" value={form.last_name} onChange={handleChange} required />
      </label>
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
      <button className="btn btn-primary" disabled={loading}>
        {loading ? t("common.loading") : t("auth.registerBtn")}
      </button>
      <p className="auth-switch">
        {t("auth.hasAccount")}{" "}
        <button type="button" className="link-btn" onClick={onBack}>
          {t("auth.login")}
        </button>
      </p>
    </form>
  );
}