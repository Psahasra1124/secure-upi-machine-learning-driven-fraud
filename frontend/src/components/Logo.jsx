import { ShieldCheck } from "lucide-react";

export default function Logo({ compact = false }) {
  return (
    <div className="flex items-center gap-3">
      <div className="grid size-10 shrink-0 place-items-center rounded-xl bg-mint-400 text-ink-950 shadow-glow">
        <ShieldCheck size={22} strokeWidth={2.4} />
      </div>
      {!compact && (
        <div>
          <p className="text-[15px] font-extrabold tracking-tight">Secure UPI</p>
          <p className="text-[10px] font-medium uppercase tracking-[0.2em] text-slate-500">
            Fraud Intelligence
          </p>
        </div>
      )}
    </div>
  );
}

