import { useState } from "react";
import { useTranslation } from "react-i18next";
import { useAuth } from "../../context/AuthContext";
import RegisterForm from "./RegisterForm";
import OtpVerify from "./OtpVerify";

export default function LoginModal({
  onSuccess,
  initialMode = "login",
  embedded = false,
  onClose,
  onRegister,
  onOtpRequired,
  onLogin,
}) {
  const { t } = useTranslation();
  const { login } = useAuth();
  const [mode, setMode] = useState(initialMode);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [pendingOtpEmail, setPendingOtpEmail] = useState("");

  const switchMode = (m) => {
    setError("");
    setMode(m);
    if (m === "login" && onLogin) onLogin();
    if (m === "register" && onRegister) onRegister();
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      await login(email, password);
      if (onSuccess) onSuccess();
    } catch {
      setError(t("auth.wrongCredentials"));
    } finally {
      setLoading(false);
    }
  };

  if (mode === "register") {
    return (
      <RegisterForm
        onOtpRequired={(em) => {
          setPendingOtpEmail(em);
          if (onOtpRequired) onOtpRequired(em);
          else setMode("otp");
        }}
        onBack={() => switchMode("login")}
      />
    );
  }

  if (mode === "otp") {
    return (
      <OtpVerify
        email={pendingOtpEmail}
        onSuccess={() => {
          if (onSuccess) onSuccess();
        }}
      />
    );
  }

  const content = (
    <form className="auth-form" onSubmit={handleLogin}>
      <h2>{t("auth.loginTitle")}</h2>
      <label>
        {t("auth.email")}
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
      </label>
      <label>
        {t("auth.password")}
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
      </label>
      {error && <p className="error-text">{error}</p>}
      <button className="btn btn-primary" disabled={loading}>
        {loading ? t("common.loading") : t("auth.loginBtn")}
      </button>
      <p className="auth-switch">
        {t("auth.noAccount")}{" "}
        <button type="button" className="link-btn" onClick={() => switchMode("register")}>
          {t("auth.register")}
        </button>
      </p>
    </form>
  );

  if (embedded) return content;

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>
          ✕
        </button>
        {content}
      </div>
    </div>
  );
}