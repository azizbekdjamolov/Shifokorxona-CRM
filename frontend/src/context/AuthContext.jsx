import { createContext, useContext, useEffect, useState } from "react";
import { getMe, register, verifyOtp, login as loginApi } from "../api/authApi";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const access = localStorage.getItem("access");
    if (!access) {
      setLoading(false);
      return;
    }
    getMe()
      .then((res) => setUser(res.data))
      .catch(() => {
        localStorage.removeItem("access");
        localStorage.removeItem("refresh");
        setUser(null);
      })
      .finally(() => setLoading(false));
  }, []);

  const setAuth = (data) => {
    localStorage.setItem("access", data.tokens.access);
    localStorage.setItem("refresh", data.tokens.refresh);
    setUser(data.user);
  };

  const registerUser = async (form) => {
    const res = await register(form);
    return res.data;
  };

  const confirmOtp = async (email, code) => {
    const res = await verifyOtp({ email, code });
    setAuth(res.data);
    return res.data;
  };

  const login = async (email, password) => {
    const res = await loginApi({ email, password });
    localStorage.setItem("access", res.data.access);
    localStorage.setItem("refresh", res.data.refresh);
    const me = await getMe();
    setUser(me.data);
    return me.data;
  };

  const logout = () => {
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");
    setUser(null);
  };

  const updateUser = async (data) => {
    const res = await getMe();
    setUser(res.data);
    return res.data;
  };

  const value = {
    user,
    setUser,
    loading,
    isAuthenticated: !!user,
    registerUser,
    confirmOtp,
    login,
    logout,
    updateUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}