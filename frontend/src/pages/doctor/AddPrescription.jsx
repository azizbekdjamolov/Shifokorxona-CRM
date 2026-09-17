import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { createPrescription } from "../../api/prescriptionsApi";
import { getDoctorTodayQueue } from "../../api/bookingsApi";

export default function AddPrescription() {
  const [searchParams] = useSearchParams();
  const [bookings, setBookings] = useState([]);
  const [bookingId, setBookingId] = useState(searchParams.get("booking") || "");
  const [form, setForm] = useState({
    medicine_name: "",
    instruction: "",
    times_per_day: 1,
    days: 1,
    image: null,
  });
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    getDoctorTodayQueue().then((res) => {
      const list = res.data.results || res.data;
      const completed = list.filter((b) => b.status === "completed");
      setBookings(completed);
      if (!bookingId && completed.length > 0) {
        setBookingId(String(completed[0].id));
      }
    });
  }, []);

  const handleChange = (e) =>
    setForm({ ...form, [e.target.name]: e.target.value });

  const handleFile = (e) =>
    setForm({ ...form, image: e.target.files[0] });

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setSuccess(false);
    const data = new FormData();
    data.append("booking", bookingId);
    data.append("medicine_name", form.medicine_name);
    data.append("instruction", form.instruction);
    data.append("times_per_day", form.times_per_day);
    data.append("days", form.days);
    if (form.image) data.append("image", form.image);
    try {
      await createPrescription(data);
      setSuccess(true);
      setForm({ medicine_name: "", instruction: "", times_per_day: 1, days: 1, image: null });
    } catch (err) {
      setError(err.response?.data?.booking?.[0] || "Retsept yozishda xatolik");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="form-page">
      <h1>Retsept yozish</h1>
      <form className="auth-form" onSubmit={submit}>
        <label>
          Bemor (yakunlangan bron)
          <select value={bookingId} onChange={(e) => setBookingId(e.target.value)} required>
            <option value="">Bemorni tanlang</option>
            {bookings.map((b) => (
              <option key={b.id} value={b.id}>
                {b.patient_name} — {b.time}
              </option>
            ))}
          </select>
        </label>
        <label>
          Dori nomi
          <input
            name="medicine_name"
            value={form.medicine_name}
            onChange={handleChange}
            required
          />
        </label>
        <label>
          Qo'llash izohi
          <textarea
            name="instruction"
            value={form.instruction}
            onChange={handleChange}
            rows={3}
            required
          />
        </label>
        <div className="form-row">
          <label>
            Kuniga necha marta
            <input
              type="number"
              name="times_per_day"
              min={1}
              max={10}
              value={form.times_per_day}
              onChange={handleChange}
              required
            />
          </label>
          <label>
            Necha kun
            <input
              type="number"
              name="days"
              min={1}
              value={form.days}
              onChange={handleChange}
              required
            />
          </label>
        </div>
        <label>
          Dori rasmi (ixtiyoriy)
          <input type="file" accept="image/*" onChange={handleFile} />
        </label>
        {success && <p className="success-message">✅ Retsept saqlandi</p>}
        {error && <p className="error-text">{error}</p>}
        <button className="btn btn-primary" disabled={loading}>
          {loading ? "Yuborilmoqda..." : "Retseptni saqlash"}
        </button>
      </form>
    </div>
  );
}