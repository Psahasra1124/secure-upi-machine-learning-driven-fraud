import { dateTime, money } from "../lib/format";

export default function TransactionTable({ transactions, loading = false }) {
  if (loading) {
    return (
      <div className="space-y-3 p-5">
        {[1, 2, 3, 4].map((item) => (
          <div key={item} className="h-12 animate-pulse rounded-xl bg-slate-100 dark:bg-white/5" />
        ))}
      </div>
    );
  }
  if (!transactions?.length) {
    return (
      <div className="px-5 py-16 text-center text-sm text-slate-500">
        No transactions found. Analyze one to begin building your risk history.
      </div>
    );
  }
  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[850px] text-left text-sm">
        <thead className="border-b bg-slate-50/70 text-[10px] uppercase tracking-[0.14em] text-slate-500 dark:border-white/10 dark:bg-white/[0.02]">
          <tr>
            <th className="px-5 py-3.5 font-semibold">Transaction</th>
            <th className="px-5 py-3.5 font-semibold">Context</th>
            <th className="px-5 py-3.5 font-semibold">Amount</th>
            <th className="px-5 py-3.5 font-semibold">Risk score</th>
            <th className="px-5 py-3.5 font-semibold">Decision</th>
          </tr>
        </thead>
        <tbody className="divide-y dark:divide-white/10">
          {transactions.map((transaction) => (
            <tr key={transaction.id} className="transition hover:bg-slate-50 dark:hover:bg-white/[0.02]">
              <td className="px-5 py-4">
                <p className="mono text-xs font-medium">UPI-{String(transaction.id).padStart(6, "0")}</p>
                <p className="mt-1 text-xs text-slate-500">{dateTime(transaction.transaction_time)}</p>
              </td>
              <td className="px-5 py-4">
                <p className="font-medium capitalize">{transaction.merchant_category}</p>
                <p className="mt-1 text-xs capitalize text-slate-500">
                  {transaction.device_type} · {transaction.location}
                </p>
              </td>
              <td className="px-5 py-4 font-semibold">{money(transaction.amount)}</td>
              <td className="px-5 py-4">
                <div className="flex items-center gap-3">
                  <div className="h-1.5 w-20 overflow-hidden rounded-full bg-slate-100 dark:bg-white/10">
                    <div
                      className={`h-full rounded-full ${
                        transaction.fraud_probability >= 0.5 ? "bg-rose-500" : "bg-mint-400"
                      }`}
                      style={{ width: `${Math.max(3, transaction.fraud_probability * 100)}%` }}
                    />
                  </div>
                  <span className="mono text-xs">
                    {(transaction.fraud_probability * 100).toFixed(1)}%
                  </span>
                </div>
              </td>
              <td className="px-5 py-4">
                <span
                  className={`inline-flex rounded-full px-2.5 py-1 text-xs font-semibold ${
                    transaction.is_fraud
                      ? "bg-rose-500/10 text-rose-600 dark:text-rose-400"
                      : "bg-mint-400/15 text-emerald-700 dark:text-mint-300"
                  }`}
                >
                  {transaction.is_fraud ? "Fraud" : "Legitimate"}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

