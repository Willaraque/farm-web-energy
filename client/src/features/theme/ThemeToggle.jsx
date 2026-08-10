import { Monitor, Moon, Sun } from "lucide-react";
import { useTheme } from "./theme-context";

const themes = [{ value: "light", label: "Tema claro", icon: Sun }, { value: "dark", label: "Tema oscuro", icon: Moon }, { value: "system", label: "Tema del sistema", icon: Monitor }];
export default function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  const index = themes.findIndex(({ value }) => value === theme);
  const CurrentIcon = themes[index].icon;
  return <button type="button" className="icon-button theme-toggle" onClick={() => setTheme(themes[(index + 1) % themes.length].value)} aria-label={`${themes[index].label}. Cambiar tema`} title={`${themes[index].label} · Cambiar tema`}><CurrentIcon size={18} /><span className="theme-indicator" aria-hidden="true" /></button>;
}
