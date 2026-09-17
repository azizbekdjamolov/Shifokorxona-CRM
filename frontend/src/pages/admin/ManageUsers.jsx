import { useEffect, useState } from "react";
import { getAdminUsers, updateAdminUser } from "../../api/authApi";

const roleNames = {
  patient: "Bemor",
  doctor: "Shifokor",
  admin: "Admin",
};

export default function ManageUsers() {
  const [users, setUsers] = useState([]);
  const [roleFilter, setRoleFilter] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    load();
  }, [roleFilter]);

  const load = () => {
    setLoading(true);
    getAdminUsers(roleFilter ? { role: roleFilter, page_size: 100 } : { page_size: 100 })
      .then((res) => setUsers(res.data.results || res.data))
      .finally(() => setLoading(false));
  };

  const changeRole = async (id, role) => {
    await updateAdminUser(id, { role });
    load();
  };

  const toggleActive = async (user) => {
    await updateAdminUser(user.id, { is_active: !user.is_active });
    load();
  };

  return (
    <div className="list-page">
      <h1>Foydalanuvchilar</h1>
      <select value={roleFilter} onChange={(e) => setRoleFilter(e.target.value)}>
        <option value="">Barcha</option>
        <option value="patient">Bemor</option>
        <option value="doctor">Shifokor</option>
        <option value="admin">Admin</option>
      </select>
      {loading && <p>Yuklanmoqda...</p>}
      <div className="card-list">
        {users.map((u) => (
          <div key={u.id} className="card user-card">
            <div className="card-head">
              <h3>{u.full_name || u.email}</h3>
              <span className={`status-badge status-${u.is_active ? "completed" : "cancelled"}`}>
                {u.is_active ? "Faol" : "Bloklangan"}
              </span>
            </div>
            <p>
              {u.email} • {u.phone}
            </p>
            <div className="card-actions">
              <select value={u.role} onChange={(e) => changeRole(u.id, e.target.value)}>
                {Object.entries(roleNames).map(([key, name]) => (
                  <option key={key} value={key}>
                    {name}
                  </option>
                ))}
              </select>
              <button className="btn" onClick={() => toggleActive(u)}>
                {u.is_active ? "Bloklash" : "Faollashtirish"}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}