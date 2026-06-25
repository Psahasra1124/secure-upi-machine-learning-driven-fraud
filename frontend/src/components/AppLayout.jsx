import {
  Activity,
  History,
  LayoutDashboard,
  LogOut,
  Menu,
  Moon,
  ScanSearch,
  Sun,
  X,
} from "lucide-react";
import { useState } from "react";
import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useTheme } from "../context/ThemeContext";
import Logo from "./Logo";

const links = [
  { to: "/dashboard", icon: LayoutDashboard, label: "Overview" },
  { to: "/predict", icon: ScanSearch, label: "Analyze transaction" },
  { to: "/transactions", icon: History, label: "Transaction history" },
];

export default function AppLayout() {
  const [open, setOpen] = useState(false);
  const { user, logout } = useAuth();
  const { dark, toggle } = useTheme();

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-ink-950">
      <aside
        className={`fixed inset-y-0 left-0 z-40 w-72 border-r bg-white p-5 transition-transform dark:border-white/10 dark:bg-ink-900 lg:translate-x-0 ${
          open ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="flex items-center justify-between">
          <Logo />
          <button className="lg:hidden" onClick={() => setOpen(false)} aria-label="Close menu">
            <X size={21} />
          </button>
        </div>

        <div className="mt-10 space-y-1">
          <p className="mb-3 px-3 text-[10px] font-bold uppercase tracking-[0.2em] text-slate-400">
            Command center
          </p>
          {links.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              onClick={() => setOpen(false)}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-xl px-3 py-3 text-sm font-medium transition ${
                  isActive
                    ? "bg-ink-950 text-white dark:bg-mint-400 dark:text-ink-950"
                    : "text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-white/5"
                }`
              }
            >
              <Icon size={18} />
              {label}
            </NavLink>
          ))}
        </div>

        <div className="absolute bottom-5 left-5 right-5">
          <div className="mb-3 flex items-center gap-2 rounded-xl border bg-mint-400/10 px-3 py-2.5 text-xs text-emerald-700 dark:border-mint-400/20 dark:text-mint-300">
            <Activity size={16} />
            <span>Detection service online</span>
          </div>
          <div className="flex items-center gap-3 border-t pt-4 dark:border-white/10">
            <div className="grid size-9 place-items-center rounded-full bg-slate-200 text-xs font-bold dark:bg-white/10">
              {user?.full_name
                ?.split(" ")
                .slice(0, 2)
                .map((word) => word[0])
                .join("")}
            </div>
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-semibold">{user?.full_name}</p>
              <p className="text-xs capitalize text-slate-500">{user?.role}</p>
            </div>
            <button
              className="text-slate-400 hover:text-rose-500"
              onClick={logout}
              title="Sign out"
            >
              <LogOut size={18} />
            </button>
          </div>
        </div>
      </aside>

      {open && (
        <button
          className="fixed inset-0 z-30 bg-ink-950/60 backdrop-blur-sm lg:hidden"
          onClick={() => setOpen(false)}
          aria-label="Close menu overlay"
        />
      )}

      <div className="lg:pl-72">
        <header className="sticky top-0 z-20 flex h-16 items-center justify-between border-b bg-slate-50/85 px-4 backdrop-blur-xl dark:border-white/10 dark:bg-ink-950/85 sm:px-8">
          <button className="lg:hidden" onClick={() => setOpen(true)} aria-label="Open menu">
            <Menu size={22} />
          </button>
          <p className="hidden text-xs font-medium text-slate-500 sm:block">
            Real-time risk operations · <span className="text-mint-500">Protected</span>
          </p>
          <button
            onClick={toggle}
            className="ml-auto grid size-9 place-items-center rounded-xl border bg-white transition hover:bg-slate-100 dark:border-white/10 dark:bg-white/5 dark:hover:bg-white/10"
            aria-label="Toggle dark mode"
          >
            {dark ? <Sun size={17} /> : <Moon size={17} />}
          </button>
        </header>
        <main className="mx-auto max-w-[1500px] p-4 sm:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

