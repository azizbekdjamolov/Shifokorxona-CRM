import { useTheme } from "../context/ThemeContext";

export default function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();
  return (
    <button className="theme-toggle" onClick={toggleTheme} title={theme === "light" ? "Qorong'u rejim" : "Yorug' rejim"}>
      {theme === "light" ? "🌙" : "☀️"}
    </button>
  );
}