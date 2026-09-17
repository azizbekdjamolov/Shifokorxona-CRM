import { useEffect, useState } from "react";
import {
  getMySchedule,
  addSchedule,
  updateSchedule,
  deleteSchedule,
} from "../../api/doctorsApi";

const weekdays = [
  { value: 0, label: "Dushanba" },
  { value: 1, label: "Seshanba" },
  { value: 2, label: "Chorshanba" },
  { value: 3, label: "Payshanba" },
  { value: 4, label: "Juma" },
  { value: 5, label: "Shanba" },
  { value: 6, label: "Yakshanba" },
];
const dayNumber = { 0: "Dushanba", 1: "Seshanba", 2: "Chorshanba", 3: "Payshanba", 4: "Juma", 5: "Shanba", 6: "Yakshanba" };

export default function Schedule() {
  const [items, setItems] = useState([]);
  const [form, setForm] = useState({
    weekday: 0,
    start_time: "09:00",
    end_time: "18:00",
    is_working: true,
  });
  const [editingId, setEditingId] = useState(null);

  useEffect(() => {
    load();
  }, []);

  const load = () => getMySchedule().then((res) => setItems(res.data.results || res.data));

  const handleChange = (e) =>
    setForm({ ...form, [e.target.name]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    const payload = {
      weekday: Number(form.weekday),
      start_time: form.start_time,
      end_time: form.end_time,
      is_working: form.is_working,
    };
    if (editingId) {
      await updateSchedule(editingId, payload);
    } else {
      await addSchedule(payload);
    }
    setEditingId(null);
    setForm({ weekday: 0, start_time: "09:00", end_time: "18:00", is_working: true });
    load();
  };

  const startEdit = (item) => {
    setEditingId(item.id);
    setForm({
      weekday: item.weekday,
      start_time: item.start_time.slice(0, 5),
      end_time: item.end_time.slice(0, 5),
      is_working: item.is_working,
    });
  };

  const remove = async (id) => {
    if (!window.confirm("Jadval yozuvini o'chirasizmi?")) return;
    await deleteSchedule(id);
    load();
  };

  return (
    <div className="list-page">
      <h1>Ish jadvali</h1>
      <form className="auth-form schedule-form" onSubmit={submit}>
        <div className="form-row">
          <label>
            Kun
            <select name="weekday" value={form.weekday} onChange={handleChange}>
              {weekdays.map((d) => (
                <option key={d.value} value={d.value}>
                  {d.label}
                </option>
              ))}
            </select>
          </label>
          <label>
            Boshlanish
            <input
              type="time"
              name="start_time"
              value={form.start_time}
              onChange={handleChange}
              required
            />
          </label>
          <label>
            Tugash
            <input
              type="time"
              name="end_time"
              value={form.end_time}
              onChange={handleChange}
              required
            />
          </label>
          <label className="checkbox-label">
            <input
              type="checkbox"
              name="is_working"
              checked={form.is_working}
              onChange={(e) => setForm({ ...form, is_working: e.target.checked })}
            />
            Ish kuni
          </label>
        </div>
        <button className="btn btn-primary">
          {editingId ? "Yangilash" : "Qo'shish"}
        </button>
        {editingId && (
          <button
            type="button"
            className="btn"
            onClick={() => {
              setEditingId(null);
              setForm({ weekday: 0, start_time: "09:00", end_time: "18:00", is_working: true });
            }}
          >
            Bekor qilish
          </button>
        )}
      </form>

      <div className="card-list">
        {items.map((item) => (
          <div key={item.id} className="card schedule-card">
            <div className="card-head">
              <h3>{dayNumber[item.weekday]}</h3>
              <span className="hint">{item.is_working ? "Ish kuni" : "Dam olish"}</span>
            </div>
            <p>
              {item.start_time.slice(0, 5)} — {item.end_time.slice(0, 5)}
            </p>
            <div className="card-actions">
              <button className="btn" onClick={() => startEdit(item)}>
                Tahrirlash
              </button>
              <button className="btn btn-danger" onClick={() => remove(item.id)}>
                O'chirish
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}