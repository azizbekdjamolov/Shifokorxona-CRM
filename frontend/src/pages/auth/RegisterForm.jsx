import { useState } from "react";
import { useAuth } from "../../context/AuthContext";

export default function RegisterForm({ onOtpRequired, onBack }) {
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
      const firstError = data
        ? Object.values(data).flat()[0]
        : "Ro'yxatdan o'tishda xatolik";
      setError(firstError || "Ro'yxatdan o'tishda xatolik");
    } finally {
      setLoading(false);
    }
  };

  const content = (
    <form className="auth-form" onSubmit={submit}>
      <h2>Ro'yxatdan o'tish</h2>
      <label>
        Ism
        <input
          name="first_name"
          value={form.first_name}
          onChange={handleChange}
          required
        />
      </label>
      <label>
        Familiya
        <input
          name="last_name"
          value={form.last_name}
          onChange={handleChange}
          required
        />
      </label>
      <label>
        Telefon
        <input
          name="phone"
          value={form.phone}
          onChange={handleChange}
          placeholder="+998..."
        />
      </label>
      <label>
        Email
        <input
          type="email"
          name="email"
          value={form.email}
          onChange={handleChange}
          required
        />
      </label>
      <label>
        Parol
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
        Parolni takrorlang
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
        {loading ? "Yuklanmoqda..." : "Ro'yxatdan o'tish"}
      </button>
      <p className="auth-switch">
        Hisobingiz bormi?{" "}
        <button type="button" className="link-btn" onClick={onBack}>
          Kirish
        </button>
      </p>
    </form>
  );

  return content;
}