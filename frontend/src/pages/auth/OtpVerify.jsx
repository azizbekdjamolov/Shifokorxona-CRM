import { useState } from "react";
import { useAuth } from "../../context/AuthContext";
import { resendOtp } from "../../api/authApi";

export default function OtpVerify({ email, onSuccess }) {
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
      setError("Kod noto'g'ri yoki muddati o'tgan");
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
      <h2>Emailni tasdiqlash</h2>
      <p>{email} manziliga yuborilgan 6 xonali kodni kiriting.</p>
      <label>
        Tasdiqlash kodi
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
        {loading ? "Yuklanmoqda..." : "Tasdiqlash"}
      </button>
      <p className="auth-switch">
        Kod kelmadimi?{" "}
        <button type="button" className="link-btn" onClick={handleResend}>
          Qayta yuborish
        </button>
      </p>
    </form>
  );
}