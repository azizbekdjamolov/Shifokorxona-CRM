import { useState } from "react";
import { useTranslation } from "react-i18next";
import { useAuth } from "../context/AuthContext";

export default function Profile() {
  const { t } = useTranslation();
  const { user, updateProfile } = useAuth();
  const [form, setForm] = useState({
    first_name: user?.first_name || "",
    last_name: user?.last_name || "",
    phone: user?.phone || "",
  });
  const [pass, setPass] = useState({
    current_password: "",
    password: "",
    confirm_password: "",
  });
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });
  const handlePassChange = (e) => setPass({ ...pass, [e.target.name]: e.target.value });

  const submitProfile = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setSuccess(false);
    try {
      await updateProfile(form);
      setSuccess(true);
    } catch (err) {
      const data = err.response?.data;
      const firstError = data ? Object.values(data).flat()[0] : null;
      setError(firstError || t("common.error"));
    } finally {
      setLoading(false);
    }
  };

  const submitPassword = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setSuccess(false);
    try {
      await updateProfile(pass);
      setPass({ current_password: "", password: "", confirm_password: "" });
      setSuccess(true);
    } catch (err) {
      const data = err.response?.data;
      const firstError = data ? Object.values(data).flat()[0] : null;
      setError(firstError || t("common.error"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="form-page profile-page">
      <h1>{t("profile.title")}</h1>
      {error && <p className="error-text">{error}</p>}
      {success && <p className="success-message">{t("profile.saved")}</p>}

      <form className="auth-form" onSubmit={submitProfile}>
        <h2>{t("profile.personalInfo")}</h2>
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
          <input value={user?.email || ""} disabled />
        </label>
        <p className="hint">{t("profile.role")}: {t(`roles.${user?.role}`)}</p>
        <button className="btn btn-primary" disabled={loading}>
          {loading ? t("common.loading") : t("common.save")}
        </button>
      </form>

      <form className="auth-form" onSubmit={submitPassword}>
        <h2>{t("profile.changePassword")}</h2>
        <label>
          {t("profile.currentPassword")}
          <input
            type="password"
            name="current_password"
            value={pass.current_password}
            onChange={handlePassChange}
            required
          />
        </label>
        <label>
          {t("profile.newPassword")}
          <input
            type="password"
            name="password"
            value={pass.password}
            onChange={handlePassChange}
            minLength={8}
            required
          />
        </label>
        <label>
          {t("profile.confirmNewPassword")}
          <input
            type="password"
            name="confirm_password"
            value={pass.confirm_password}
            onChange={handlePassChange}
            minLength={8}
            required
          />
        </label>
        <button className="btn btn-primary" disabled={loading}>
          {loading ? t("common.loading") : t("profile.updatePassword")}
        </button>
      </form>
    </div>
  );
}