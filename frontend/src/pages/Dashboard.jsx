import {
  ArrowRight,
  BadgeIndianRupee,
  CircleAlert,
  ReceiptIndianRupee,
  ShieldCheck,
} from "lucide-react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import StatCard from "../components/StatCard";
import TransactionTable from "../components/TransactionTable";
import api from "../lib/api";
import { apiError, money, number } from "../lib/format";

const emptySummary = {
  total_transactions: 0,
  fraudulent_transactions: 0,
  legitimate_transactions: 0,
  fraud_percentage: 0,
  total_amount: 0,
  blocked_amount: 0,
};

export default function Dashboard() {
  const [summary, setSummary] = useState(emptySummary);
  const [trend, setTrend] = useState([]);
  const [categories, setCategories] = useState([]);
  const [recent, setRecent] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([
      api.get("/analytics/summary"),
      api.get("/analytics/trend?days=14"),
      api.get("/analytics/categories"),
      api.get("/transactions?page=1&page_size=6"),
    ])
      .then(([summaryResponse, trendResponse, categoryResponse, transactionResponse]) => {
        setSummary(summaryResponse.data);
        setTrend(trendResponse.data);
        setCategories(categoryResponse.data);
        setRecent(transactionResponse.data.items);
      })
      .catch((requestError) => setError(apiError(requestError, "Unable to load analytics")))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="animate-rise space-y-7">
      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-end">
        <div>
          <p className="mono text-xs uppercase tracking-[0.18em] text-mint-500">Risk overview</p>
          <h1 className="mt-2 text-3xl font-extrabold tracking-tight">Transaction intelligence</h1>
          <p className="mt-2 text-sm text-slate-500">
            Live operating view of model decisions and payment behavior.
          </p>
        </div>
        <Link to="/predict" className="button-primary">
          Analyze a transaction <ArrowRight size={17} />
        </Link>
      </div>

      {error && <div className="rounded-xl bg-rose-500/10 p-3 text-sm text-rose-600">{error}</div>}

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          label="Total transactions"
          value={number(summary.total_transactions)}
          detail={`${money(summary.total_amount)} processed`}
          icon={ReceiptIndianRupee}
          tone="blue"
        />
        <StatCard
          label="Fraud detected"
          value={number(summary.fraudulent_transactions)}
          detail={`${summary.fraud_percentage}% of analyzed volume`}
          icon={CircleAlert}
          tone="rose"
        />
        <StatCard
          label="Legitimate"
          value={number(summary.legitimate_transactions)}
          detail="Transactions cleared"
          icon={ShieldCheck}
          tone="mint"
        />
        <StatCard
          label="At-risk value"
          value={money(summary.blocked_amount)}
          detail="Potential exposure identified"
          icon={BadgeIndianRupee}
          tone="amber"
        />
      </section>

      <section className="grid gap-5 xl:grid-cols-[1.6fr_1fr]">
        <div className="card p-5">
          <div className="mb-5">
            <h2 className="font-bold">Detection activity</h2>
            <p className="mt-1 text-xs text-slate-500">Total and fraudulent transactions · 14 days</p>
          </div>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trend}>
                <defs>
                  <linearGradient id="totalGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#38e6ad" stopOpacity={0.28} />
                    <stop offset="95%" stopColor="#38e6ad" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#94a3b822" />
                <XAxis dataKey="label" tickFormatter={(value) => value.slice(5)} tick={{ fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 11 }} axisLine={false} tickLine={false} allowDecimals={false} />
                <Tooltip contentStyle={{ borderRadius: 12, border: "1px solid #94a3b833" }} />
                <Area type="monotone" dataKey="total" stroke="#12c98f" fill="url(#totalGradient)" strokeWidth={2.5} />
                <Area type="monotone" dataKey="fraud" stroke="#f43f5e" fill="transparent" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card p-5">
          <div className="mb-5">
            <h2 className="font-bold">Category risk</h2>
            <p className="mt-1 text-xs text-slate-500">Fraud signals by merchant group</p>
          </div>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={categories} layout="vertical" margin={{ left: 10 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#94a3b822" />
                <XAxis type="number" hide />
                <YAxis dataKey="category" type="category" width={80} tick={{ fontSize: 11 }} axisLine={false} tickLine={false} />
                <Tooltip contentStyle={{ borderRadius: 12, border: "1px solid #94a3b833" }} />
                <Bar dataKey="fraud" fill="#f43f5e" radius={[0, 6, 6, 0]} barSize={13} />
                <Bar dataKey="total" fill="#38e6ad" radius={[0, 6, 6, 0]} barSize={13} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </section>

      <section className="card overflow-hidden">
        <div className="flex items-center justify-between border-b px-5 py-4 dark:border-white/10">
          <div>
            <h2 className="font-bold">Recent transactions</h2>
            <p className="mt-1 text-xs text-slate-500">Latest model decisions across the platform</p>
          </div>
          <Link className="text-xs font-semibold text-emerald-600 dark:text-mint-400" to="/transactions">
            View all
          </Link>
        </div>
        <TransactionTable transactions={recent} loading={loading} />
      </section>
    </div>
  );
}

