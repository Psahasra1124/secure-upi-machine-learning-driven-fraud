import { Download, Search } from "lucide-react";
import { useEffect, useState } from "react";
import TransactionTable from "../components/TransactionTable";
import api, { API_URL } from "../lib/api";
import { apiError } from "../lib/format";

export default function History() {
  const [data, setData] = useState({ items: [], total: 0, page: 1, pages: 0 });
  const [search, setSearch] = useState("");
  const [fraud, setFraud] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = (page = 1) => {
    setLoading(true);
    setError("");
    const params = new URLSearchParams({ page: String(page), page_size: "15" });
    if (search) params.set("search", search);
    if (fraud) params.set("fraud", fraud);
    api
      .get(`/transactions?${params}`)
      .then((response) => setData(response.data))
      .catch((requestError) => setError(apiError(requestError, "Unable to load transactions")))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    const timer = setTimeout(() => load(1), 250);
    return () => clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [search, fraud]);

  const exportCsv = async () => {
    const params = new URLSearchParams();
    if (search) params.set("search", search);
    if (fraud) params.set("fraud", fraud);
    const response = await fetch(`${API_URL}/transactions/export.csv?${params}`, {
      headers: { Authorization: `Bearer ${localStorage.getItem("secure_upi_token")}` },
    });
    const blob = await response.blob();
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "secure-upi-report.csv";
    link.click();
    URL.revokeObjectURL(link.href);
  };

  return (
    <div className="animate-rise space-y-7">
      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-end">
        <div>
          <p className="mono text-xs uppercase tracking-[0.18em] text-mint-500">Audit trail</p>
          <h1 className="mt-2 text-3xl font-extrabold tracking-tight">Transaction history</h1>
          <p className="mt-2 text-sm text-slate-500">{data.total} recorded model decisions</p>
        </div>
        <button className="button-secondary" onClick={exportCsv}>
          <Download size={17} /> Export CSV
        </button>
      </div>

      <section className="card overflow-hidden">
        <div className="flex flex-col gap-3 border-b p-4 dark:border-white/10 sm:flex-row">
          <div className="relative flex-1">
            <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" size={17} />
            <input
              className="input pl-10"
              placeholder="Search category, device, or location..."
              value={search}
              onChange={(event) => setSearch(event.target.value)}
            />
          </div>
          <select className="input sm:w-48" value={fraud} onChange={(event) => setFraud(event.target.value)}>
            <option value="">All decisions</option>
            <option value="true">Fraud only</option>
            <option value="false">Legitimate only</option>
          </select>
        </div>
        {error && <div className="m-4 rounded-xl bg-rose-500/10 p-3 text-sm text-rose-600">{error}</div>}
        <TransactionTable transactions={data.items} loading={loading} />
        <div className="flex items-center justify-between border-t px-5 py-4 text-xs dark:border-white/10">
          <p className="text-slate-500">
            Page {data.page} of {Math.max(data.pages, 1)}
          </p>
          <div className="flex gap-2">
            <button className="button-secondary px-3 py-2" disabled={data.page <= 1} onClick={() => load(data.page - 1)}>
              Previous
            </button>
            <button className="button-secondary px-3 py-2" disabled={data.page >= data.pages} onClick={() => load(data.page + 1)}>
              Next
            </button>
          </div>
        </div>
      </section>
    </div>
  );
}
