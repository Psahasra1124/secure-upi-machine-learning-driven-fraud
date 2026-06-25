import { ArrowRight, LoaderCircle } from "lucide-react";
import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import AuthShell from "../components/AuthShell";
import { useAuth } from "../context/AuthContext";
import { apiError } from "../lib/format";

export default function Login() {
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const { login, loading } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const submit = async (event) => {
    event.preventDefault();
    setError("");
    try {
      await login(form.email, form.password);
      navigate(location.state?.from || "/dashboard", { replace: true });
    } catch (requestError) {
      setError(apiError(requestError, "Unable to sign in"));
    }
  };

  return (
    <AuthShell title="Welcome back" subtitle="Sign in to review risk, transactions, and live model decisions.">
      <form onSubmit={submit} className="space-y-5">
        {error && <div className="rounded-xl bg-rose-500/10 p-3 text-sm text-rose-600">{error}</div>}
        <div>
          <label className="label" htmlFor="email">Email address</label>
          <input
            id="email"
            type="email"
            className="input"
            placeholder="you@company.com"
            required
            value={form.email}
            onChange={(event) => setForm({ ...form, email: event.target.value })}
          />
        </div>
        <div>
          <label className="label" htmlFor="password">Password</label>
          <input
            id="password"
            type="password"
            className="input"
            placeholder="Your secure password"
            required
            value={form.password}
            onChange={(event) => setForm({ ...form, password: event.target.value })}
          />
        </div>
        <button className="button-primary w-full" disabled={loading}>
          {loading ? <LoaderCircle className="animate-spin" size={18} /> : <>Sign in <ArrowRight size={18} /></>}
        </button>
      </form>
      <p className="mt-7 text-center text-sm text-slate-500">
        New to Secure UPI?{" "}
        <Link className="font-semibold text-emerald-600 dark:text-mint-400" to="/register">
          Create an account
        </Link>
      </p>
    </AuthShell>
  );
}

