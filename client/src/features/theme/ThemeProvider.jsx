import { useEffect, useMemo, useState } from "react";
import PropTypes from "prop-types";
import { ThemeContext } from "./theme-context";

const STORAGE_KEY = "wac-theme";
const mediaQuery = "(prefers-color-scheme: dark)";
const getStoredTheme = () => {
  const stored = localStorage.getItem(STORAGE_KEY);
  return ["light", "dark", "system"].includes(stored) ? stored : "system";
};
const resolveTheme = (preference) =>
  preference === "system"
    ? window.matchMedia(mediaQuery).matches
      ? "dark"
      : "light"
    : preference;

export default function ThemeProvider({ children }) {
  const [theme, setTheme] = useState(getStoredTheme);
  const [resolvedTheme, setResolvedTheme] = useState(() => resolveTheme(theme));
  useEffect(() => {
    const query = window.matchMedia(mediaQuery);
    const applyTheme = () => {
      const resolved = resolveTheme(theme);
      document.documentElement.dataset.theme = resolved;
      document.documentElement.style.colorScheme = resolved;
      setResolvedTheme(resolved);
    };
    applyTheme();
    localStorage.setItem(STORAGE_KEY, theme);
    query.addEventListener("change", applyTheme);
    return () => query.removeEventListener("change", applyTheme);
  }, [theme]);
  const value = useMemo(
    () => ({ theme, resolvedTheme, setTheme }),
    [theme, resolvedTheme],
  );
  return (
    <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>
  );
}
ThemeProvider.propTypes = { children: PropTypes.node.isRequired };
