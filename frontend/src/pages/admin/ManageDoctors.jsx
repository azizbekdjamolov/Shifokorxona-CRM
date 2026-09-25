import { useEffect, useState } from "react";
import {
  getAdminDoctors,
  createDoctor,
  toggleDoctor,
  getSpecialties,
} from "../../api/doctorsApi";
import { getAdminUsers } from "../../api/authApi";

export default function ManageDoctors() {
  const [doctors, setDoctors] = useState([]);
  const [users, setUsers] = useState([]);
  const [specialties, setSpecialties] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    user_id: "",
    specialty: "",
    bio: "",
    experience_years: 0,
    price: 0,
    photo: null,
  });
  const [error, setError] = useState("");

  useEffect(() => {
    load();
    getSpecialties().then((res) => setSpecialties(res.data.results || res.data));
    getAdminUsers({ page_size: 100, role: "patient" }).then((res) =>
      setUsers(res.data.results || res.data)
    );
  }, []);

  const load = () =>
    getAdminDoctors({ page_size: 100 }).then((res) => setDoctors(res.data.results || res.data));

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handlePhoto = (e) => setForm({ ...form, photo: e.target.files[0] });

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    const data = new FormData();
    data.append("user_id", form.user_id);
    if (form.specialty) data.append("specialty", form.specialty);
    data.append("bio", form.bio || "");
    data.append("experience_years", form.experience_years || 0);
    data.append("price", form.price || 0);
    if (form.photo) data.append("photo", form.photo);
    try {
      await createDoctor(data);
      setShowForm(false);
      setForm({ user_id: "", specialty: "", bio: "", experience_years: 0, price: 0, photo: null });
      load();
    } catch (err) {
      const data = err.response?.data;
      setError(data ? Object.values(data).flat()[0] : "Shifokor qo'shishda xatolik");
    }
  };

  const toggle = async (d) => {
    await toggleDoctor(d.id, { is_active: !d.is_active });
    load();
  };

  return (
    <div className="list-page">
      <h1>Shifokorlar</h1>
      <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
        {showForm ? "Yopish" : "+ Shifokor qo'shish"}
      </button>

      {showForm && (
        <form className="auth-form" onSubmit={submit}>
          <label>
            Foydalanuvchi (bemor)
            <select name="user_id" value={form.user_id} onChange={handleChange} required>
              <option value="">Foydalanuvchini tanlang</option>
              {users.map((u) => (
                <option key={u.id} value={u.id}>
                  {u.full_name || u.email}
                </option>
              ))}
            </select>
          </label>
          <label>
            Yo'nalish
            <select name="specialty" value={form.specialty} onChange={handleChange}>
              <option value="">Tanlash</option>
              {specialties.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            Bio
            <textarea name="bio" value={form.bio} onChange={handleChange} rows={3} />
          </label>
          <div className="form-row">
            <label>
              Tajriba (yil)
              <input
                type="number"
                name="experience_years"
                value={form.experience_years}
                onChange={handleChange}
              />
            </label>
            <label>
              Narx
              <input type="number" name="price" value={form.price} onChange={handleChange} />
            </label>
          </div>
          <label>
            Foto (ixtiyoriy)
            <input type="file" accept="image/*" onChange={handlePhoto} />
          </label>
          {error && <p className="error-text">{error}</p>}
          <button className="btn btn-primary">Saqlash</button>
        </form>
      )}

      <div className="card-list">
        {doctors.map((d) => (
          <div key={d.id} className="card doctor-admin-card">
            <div className="card-head">
              <h3>Dr. {d.user?.full_name}</h3>
              <span className={`status-badge status-${d.is_active ? "completed" : "cancelled"}`}>
                {d.is_active ? "Faol" : "Nofaol"}
              </span>
            </div>
            <p>
              {d.specialty_name} • Tajriba: {d.experience_years} yil • ⭐ {d.average_rating}
            </p>
            <div className="card-actions">
              <button className="btn" onClick={() => toggle(d)}>
                {d.is_active ? "Nofaol qilish" : "Faollashtirish"}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}