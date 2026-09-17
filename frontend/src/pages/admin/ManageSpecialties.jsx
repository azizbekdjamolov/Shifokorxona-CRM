import { useEffect, useState } from "react";
import {
  getSpecialties,
  createSpecialty,
  updateSpecialty,
  deleteSpecialty,
} from "../../api/doctorsApi";

export default function ManageSpecialties() {
  const [items, setItems] = useState([]);
  const [form, setForm] = useState({ name: "", slug: "", description: "", icon: "" });
  const [editingId, setEditingId] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    load();
  }, []);

  const load = () => getSpecialties().then((res) => setItems(res.data.results || res.data));

  const makeSlug = (name) =>
    name
      .toLowerCase()
      .replace(/['"]/g, "")
      .replace(/\s+/g, "-")
      .replace(/[^a-z0-9-]/g, "");

  const handleChange = (e) => {
    const next = { ...form, [e.target.name]: e.target.value };
    if (e.target.name === "name" && !form.slug) next.slug = makeSlug(e.target.value);
    setForm(next);
  };

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      if (editingId) {
        await updateSpecialty(editingId, form);
      } else {
        await createSpecialty(form);
      }
      setForm({ name: "", slug: "", description: "", icon: "" });
      setEditingId(null);
      load();
    } catch (err) {
      setError(err.response?.data?.name?.[0] || "Yo'nalishni saqlashda xatolik");
    }
  };

  const startEdit = (item) => {
    setEditingId(item.id);
    setForm({
      name: item.name,
      slug: item.slug,
      description: item.description,
      icon: item.icon,
    });
  };

  const remove = async (id) => {
    if (!window.confirm("Yo'nalishni o'chirasizmi?")) return;
    await deleteSpecialty(id);
    load();
  };

  return (
    <div className="list-page">
      <h1>Yo'nalishlar</h1>
      <form className="auth-form" onSubmit={submit}>
        <div className="form-row">
          <label>
            Nomi
            <input name="name" value={form.name} onChange={handleChange} required />
          </label>
          <label>
            Slug
            <input name="slug" value={form.slug} onChange={handleChange} required />
          </label>
          <label>
            Icon (emoji)
            <input name="icon" value={form.icon} onChange={handleChange} />
          </label>
        </div>
        <label>
          Tavsif
          <textarea name="description" value={form.description} onChange={handleChange} rows={2} />
        </label>
        {error && <p className="error-text">{error}</p>}
        <button className="btn btn-primary">{editingId ? "Yangilash" : "Qo'shish"}</button>
        {editingId && (
          <button
            type="button"
            className="btn"
            onClick={() => {
              setEditingId(null);
              setForm({ name: "", slug: "", description: "", icon: "" });
            }}
          >
            Bekor qilish
          </button>
        )}
      </form>

      <div className="card-list">
        {items.map((s) => (
          <div key={s.id} className="card specialty-admin-card">
            <div className="card-head">
              <h3>
                {s.icon || "🏥"} {s.name}
              </h3>
              <span className="hint">{s.slug}</span>
            </div>
            <p>{s.description}</p>
            <div className="card-actions">
              <button className="btn" onClick={() => startEdit(s)}>
                Tahrirlash
              </button>
              <button className="btn btn-danger" onClick={() => remove(s.id)}>
                O'chirish
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}