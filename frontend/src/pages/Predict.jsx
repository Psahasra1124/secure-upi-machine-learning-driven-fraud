import {
  AlertTriangle,
  CheckCircle2,
  ChevronRight,
  LoaderCircle,
  ScanSearch,
  Sparkles,
} from "lucide-react";
import { useState } from "react";
import api from "../lib/api";
import { apiError, money } from "../lib/format";

const localNow = () => {
  const now = new Date();
  now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
  return now.toISOString().slice(0, 16);
};

const initialForm = {
  amount: "",
  time: localNow(),
  merchant_category: "grocery",
  device_type: "android",
  location: "Bengaluru",
  transaction_frequency: "1",
};

export default function Predict() {
  const [form, setForm] = useState(initialForm);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const update = (key) => (event) => setForm({ ...form, [key]: event.target.value });

  const submit = async (event) => {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      const { data } = await api.post("/predictions", {
        ...form,
        amount: Number(form.amount),
        time: new Date(form.time).toISOString(),
        transaction_frequency: Number(form.transaction_frequency),
      });
      setResult(data);
    } catch (requestError) {
      setError(apiError(requestError, "Unable to analyze transaction"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="animate-rise">
      <div className="mb-7">
        <p className="mono text-xs uppercase tracking-[0.18em] text-mint-500">Real-time scoring</p>
        <h1 className="mt-2 text-3xl font-extrabold tracking-tight">Analyze a transaction</h1>
        <p className="mt-2 text-sm text-slate-500">
          Submit payment context for an immediate risk decision and feature-level explanation.
        </p>
      </div>

      <div className="grid gap-6 xl:grid-cols-[1fr_0.9fr]">
        <form onSubmit={submit} className="card p-5 sm:p-7">
          <div className="mb-7 flex items-center gap-3 border-b pb-5 dark:border-white/10">
            <div className="grid size-10 place-items-center rounded-xl bg-mint-400/15 text-emerald-600 dark:text-mint-300">
              <ScanSearch size={20} />
            </div>
            <div>
              <h2 className="font-bold">Transaction context</h2>
              <p className="mt-0.5 text-xs text-slate-500">All fields are used by the risk model</p>
            </div>
          </div>
          {error && <div className="mb-5 rounded-xl bg-rose-500/10 p-3 text-sm text-rose-600">{error}</div>}
          <div className="grid gap-5 sm:grid-cols-2">
            <div>
              <label className="label">Amount (INR)</label>
              <input className="input" type="number" min="1" step="0.01" required placeholder="5,000" value={form.amount} onChange={update("amount")} />
            </div>
            <div>
              <label className="label">Transaction time</label>
              <input className="input" type="datetime-local" required value={form.time} onChange={update("time")} />
            </div>
            <div>
              <label className="label">Merchant category</label>
              <select className="input" value={form.merchant_category} onChange={update("merchant_category")}>
                {["grocery", "utilities", "food", "travel", "shopping", "gaming", "crypto", "cash withdrawal"].map((option) => (
                  <option key={option} value={option}>{option.replace(/\b\w/g, (letter) => letter.toUpperCase())}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="label">Device type</label>
              <select className="input" value={form.device_type} onChange={update("device_type")}>
                {["android", "ios", "web", "emulator", "rooted", "unknown"].map((option) => (
                  <option key={option}>{option}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="label">Location</label>
              <input className="input" required placeholder="Bengaluru" value={form.location} onChange={update("location")} />
            </div>
            <div>
              <label className="label">Transactions in last hour</label>
              <input className="input" type="number" min="0" max="10000" required value={form.transaction_frequency} onChange={update("transaction_frequency")} />
            </div>
          </div>
          <button className="button-primary mt-7 w-full sm:w-auto" disabled={loading}>
            {loading ? <><LoaderCircle className="animate-spin" size={18} /> Scoring transaction</> : <>Run fraud analysis <ChevronRight size={18} /></>}
          </button>
        </form>

        <section className="card min-h-[470px] overflow-hidden">
          {!result ? (
            <div className="flex h-full min-h-[470px] flex-col items-center justify-center px-8 text-center">
              <div className="grid size-16 place-items-center rounded-2xl bg-slate-100 text-slate-400 dark:bg-white/5">
                <Sparkles size={26} />
              </div>
              <h2 className="mt-5 font-bold">Awaiting transaction</h2>
              <p className="mt-2 max-w-xs text-sm leading-6 text-slate-500">
                Your risk score, decision, and SHAP feature contributions will appear here.
              </p>
            </div>
          ) : (
            <div>
              <div className={`p-6 text-white ${result.is_fraud ? "bg-rose-600" : "bg-emerald-600"}`}>
                <div className="flex items-center gap-3">
                  {result.is_fraud ? <AlertTriangle size={24} /> : <CheckCircle2 size={24} />}
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-[0.15em] opacity-80">Model decision</p>
                    <h2 className="mt-1 text-2xl font-extrabold">{result.prediction}</h2>
                  </div>
                </div>
                <div className="mt-6 flex items-end justify-between">
                  <div>
                    <p className="text-xs opacity-75">Fraud probability</p>
                    <p className="mono mt-1 text-4xl font-medium">{(result.probability * 100).toFixed(1)}%</p>
                  </div>
                  <p className="mono rounded-lg bg-black/15 px-2.5 py-1.5 text-[10px]">
                    {result.model_version}
                  </p>
                </div>
              </div>
              <div className="p-6">
                <div className="mb-4 flex items-center justify-between">
                  <h3 className="font-bold">Why this decision?</h3>
                  <span className="text-[10px] font-semibold uppercase tracking-[0.12em] text-slate-400">SHAP impact</span>
                </div>
                <div className="space-y-3">
                  {result.explanation.map((item, index) => (
                    <div key={`${item.feature}-${index}`} className="rounded-xl border p-3 dark:border-white/10">
                      <div className="flex items-center justify-between gap-4">
                        <p className="text-sm font-medium">{item.feature}</p>
                        <span className={`mono text-xs font-medium ${item.impact > 0 ? "text-rose-500" : "text-emerald-500"}`}>
                          {item.impact > 0 ? "+" : ""}{item.impact.toFixed(3)}
                        </span>
                      </div>
                      <div className="mt-2 h-1 overflow-hidden rounded-full bg-slate-100 dark:bg-white/10">
                        <div
                          className={`h-full rounded-full ${item.impact > 0 ? "bg-rose-500" : "bg-mint-400"}`}
                          style={{ width: `${Math.min(100, Math.max(5, Math.abs(item.impact) * 35))}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
                <p className="mt-5 text-xs leading-5 text-slate-500">
                  Transaction #{result.transaction_id} · Threshold {(result.threshold * 100).toFixed(0)}% · Amount {money(form.amount)}
                </p>
              </div>
            </div>
          )}
        </section>
      </div>
    </div>
  );
}

