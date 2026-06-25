import { createContext, useContext, useEffect, useState } from "react";

const ThemeContext = createContext(null);

export function ThemeProvider({ children }) {
  const [dark, setDark] = useState(
    () =>
      localStorage.getItem("secure_upi_theme") === "dark" ||
      (!localStorage.getItem("secure_upi_theme") &&
        window.matchMedia("(prefers-color-scheme: dark)").matches),
  );

  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
    localStorage.setItem("secure_upi_theme", dark ? "dark" : "light");
  }, [dark]);

  const value = { dark, toggle: () => setDark((value) => !value) };
  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

export const useTheme = () => useContext(ThemeContext);
