import { ArrowRight, LoaderCircle } from "lucide-react";
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import AuthShell from "../components/AuthShell";
import { useAuth } from "../context/AuthContext";
import { apiError } from "../lib/format";

export default function Register() {
  const [form, setForm] = useState({ full_name: "", email: "", password: "" });
  const [error, setError] = useState("");
  const { register, loading } = useAuth();
  const navigate = useNavigate();

  const submit = async (event) => {
    event.preventDefault();
    setError("");
    try {
      await register(form);
      navigate("/dashboard");
    } catch (requestError) {
      setError(apiError(requestError, "Unable to create account"));
    }
  };

  return (
    <AuthShell title="Create your account" subtitle="Start analyzing UPI transactions with explainable fraud intelligence.">
      <form onSubmit={submit} className="space-y-4">
        {error && <div className="rounded-xl bg-rose-500/10 p-3 text-sm text-rose-600">{error}</div>}
        <div>
          <label className="label" htmlFor="name">Full name</label>
          <input
            id="name"
            className="input"
            placeholder="Your name"
            minLength={2}
            required
            value={form.full_name}
            onChange={(event) => setForm({ ...form, full_name: event.target.value })}
          />
        </div>
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
            placeholder="At least 8 characters"
            minLength={8}
            required
            value={form.password}
            onChange={(event) => setForm({ ...form, password: event.target.value })}
          />
        </div>
        <button className="button-primary w-full" disabled={loading}>
          {loading ? <LoaderCircle className="animate-spin" size={18} /> : <>Create account <ArrowRight size={18} /></>}
        </button>
      </form>
      <p className="mt-7 text-center text-sm text-slate-500">
        Already registered?{" "}
        <Link className="font-semibold text-emerald-600 dark:text-mint-400" to="/login">
          Sign in
        </Link>
      </p>
    </AuthShell>
  );
}

