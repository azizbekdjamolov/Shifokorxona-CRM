import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { createPrescription } from "../../api/prescriptionsApi";
import { getDoctorTodayQueue } from "../../api/bookingsApi";
import { getPatients } from "../../api/authApi";

export default function AddPrescription() {
  const [searchParams] = useSearchParams();
  const [bookings, setBookings] = useState([]);
  const [patients, setPatients] = useState([]);
  const [patientId, setPatientId] = useState("");
  const [search, setSearch] = useState("");
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
    getPatients({ page_size: 100 }).then((res) => {
      setPatients(res.data.results || res.data);
    });
  }, []);

  const filteredPatients = useMemo(() => {
    const q = search.trim().toLowerCase();
    if (!q) return patients;
    return patients.filter((p) =>
      [p.full_name, p.first_name, p.last_name, p.email, p.phone]
        .filter(Boolean)
        .some((v) => String(v).toLowerCase().includes(q))
    );
  }, [patients, search]);

  const handleChange = (e) =>
    setForm({ ...form, [e.target.name]: e.target.value });

  const handleFile = (e) =>
    setForm({ ...form, image: e.target.files[0] });

  const submit = async (e) => {
    e.preventDefault();
    if (!patientId) {
      setError("Bemor tanlang");
      return;
    }
    setLoading(true);
    setError("");
    setSuccess(false);
    const data = new FormData();
    if (bookingId) data.append("booking", bookingId);
    data.append("patient", patientId);
    data.append("medicine_name", form.medicine_name);
    data.append("instruction", form.instruction);
    data.append("times_per_day", form.times_per_day);
    data.append("days", form.days);
    if (form.image) data.append("image", form.image);
    try {
      await createPrescription(data);
      setSuccess(true);
      setForm({ medicine_name: "", instruction: "", times_per_day: 1, days: 1, image: null });
      setPatientId("");
      setSearch("");
    } catch (err) {
      setError(
        err.response?.data?.patient?.[0] ||
          err.response?.data?.booking?.[0] ||
          "Retsept yozishda xatolik"
      );
    } finally {
      setLoading(false);
    }
  };

  const selectedPatient = patients.find((p) => String(p.id) === String(patientId));

  return (
    <div className="form-page">
      <h1>Retsept yozish</h1>
      <form className="auth-form" onSubmit={submit}>
        <label>
          Bemor (barcha ro'yxatdan o'tganlar)
          <input
            type="search"
            placeholder="Ism, familiya, email yoki telefon bo'yicha qidiring..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPatientId("");
            }}
            autoComplete="off"
          />
          {selectedPatient ? (
            <span className="patient-picked">
              ✅ {selectedPatient.full_name} — {selectedPatient.email || selectedPatient.phone}
            </span>
          ) : (
            <div className="patient-search-list">
              {filteredPatients.length === 0 && (
                <p className="form-hint">Hech qanday bemor topilmadi</p>
              )}
              {filteredPatients.map((p) => (
                <button
                  type="button"
                  key={p.id}
                  className="patient-search-item"
                  onClick={() => {
                    setPatientId(String(p.id));
                    setSearch(p.full_name);
                  }}
                >
                  <span className="patient-item-name">{p.full_name}</span>
                  <span className="patient-item-meta">
                    {p.email} {p.phone ? `• ${p.phone}` : ""}
                  </span>
                </button>
              ))}
            </div>
          )}
        </label>
        <label>
          Bron (ixtiyoriy — yakunlanganlar)
          <select value={bookingId} onChange={(e) => setBookingId(e.target.value)}>
            <option value="">Hech qanday bron</option>
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