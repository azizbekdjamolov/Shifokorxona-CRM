import { useState } from "react";
import { useTranslation } from "react-i18next";
import { useAuth } from "../../context/AuthContext";
import { resendOtp } from "../../api/authApi";

export default function OtpVerify({ email, onSuccess }) {
  const { t } = useTranslation();
  const { confirmOtp } = useAuth();
  const [code, setCode] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      await confirmOtp(email, code);
      if (onSuccess) onSuccess();
    } catch {
      setError(t("auth.wrongCode"));
    } finally {
      setLoading(false);
    }
  };

  const handleResend = async () => {
    await resendOtp(email);
    setError("");
  };

  return (
    <form className="auth-form" onSubmit={submit}>
      <h2>{t("auth.verifyTitle")}</h2>
      <p>
        {email} {t("auth.verifyText")}
      </p>
      <label>
        {t("auth.code")}
        <input
          value={code}
          onChange={(e) => setCode(e.target.value)}
          maxLength={6}
          pattern="[0-9]{6}"
          required
        />
      </label>
      {error && <p className="error-text">{error}</p>}
      <button className="btn btn-primary" disabled={loading}>
        {loading ? t("common.loading") : t("auth.verifyBtn")}
      </button>
      <p className="auth-switch">
        {t("auth.codeDidntArrive")}{" "}
        <button type="button" className="link-btn" onClick={handleResend}>
          {t("auth.resend")}
        </button>
      </p>
    </form>
  );
}