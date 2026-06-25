export default function StatCard({ label, value, detail, icon: Icon, tone = "mint" }) {
  const tones = {
    mint: "bg-mint-400/15 text-emerald-600 dark:text-mint-300",
    rose: "bg-rose-500/10 text-rose-600 dark:text-rose-400",
    amber: "bg-amber-500/10 text-amber-600 dark:text-amber-400",
    blue: "bg-blue-500/10 text-blue-600 dark:text-blue-400",
  };
  return (
    <div className="card p-5">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.13em] text-slate-500">{label}</p>
          <p className="mt-3 text-3xl font-extrabold tracking-tight">{value}</p>
          <p className="mt-2 text-xs text-slate-500">{detail}</p>
        </div>
        <div className={`grid size-10 place-items-center rounded-xl ${tones[tone]}`}>
          <Icon size={20} />
        </div>
      </div>
    </div>
  );
}

