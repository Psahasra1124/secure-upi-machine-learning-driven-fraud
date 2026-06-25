import { CheckCircle2, Fingerprint, Shield, Sparkles } from "lucide-react";
import Logo from "./Logo";

export default function AuthShell({ title, subtitle, children }) {
  return (
    <main className="min-h-screen bg-ink-950 text-white">
      <div className="grid min-h-screen lg:grid-cols-[1.1fr_0.9fr]">
        <section className="relative hidden overflow-hidden border-r border-white/10 p-12 lg:flex lg:flex-col">
          <div className="absolute -left-32 top-20 size-96 rounded-full bg-mint-400/10 blur-3xl" />
          <div className="absolute bottom-0 right-0 size-[28rem] rounded-full bg-cyan-500/10 blur-3xl" />
          <Logo />
          <div className="relative my-auto max-w-xl">
            <div className="mb-8 inline-flex items-center gap-2 rounded-full border border-mint-400/20 bg-mint-400/10 px-3 py-1.5 text-xs font-semibold text-mint-300">
              <Sparkles size={14} />
              Explainable AI, built for trust
            </div>
            <h1 className="text-5xl font-extrabold leading-[1.05] tracking-[-0.04em]">
              Every payment tells a story.
              <span className="block text-mint-400">We read the risk.</span>
            </h1>
            <p className="mt-6 max-w-lg text-base leading-7 text-slate-400">
              Detect suspicious UPI behavior in real time with an ensemble machine-learning
              workflow and human-readable feature explanations.
            </p>
            <div className="mt-10 grid grid-cols-3 gap-4">
              {[
                [Fingerprint, "Context-aware"],
                [Shield, "JWT protected"],
                [CheckCircle2, "Auditable"],
              ].map(([Icon, label]) => (
                <div key={label} className="rounded-2xl border border-white/10 bg-white/5 p-4">
                  <Icon className="mb-4 text-mint-400" size={21} />
                  <p className="text-xs font-semibold text-slate-300">{label}</p>
                </div>
              ))}
            </div>
          </div>
          <p className="text-xs text-slate-600">Secure UPI · Risk intelligence platform</p>
        </section>

        <section className="flex items-center justify-center bg-slate-50 px-5 py-10 text-slate-900 dark:bg-ink-950 dark:text-white">
          <div className="w-full max-w-md animate-rise">
            <div className="mb-10 lg:hidden">
              <Logo />
            </div>
            <p className="mono mb-2 text-xs uppercase tracking-[0.18em] text-mint-500">
              Secure access
            </p>
            <h2 className="text-3xl font-extrabold tracking-tight">{title}</h2>
            <p className="mt-2 text-sm leading-6 text-slate-500 dark:text-slate-400">{subtitle}</p>
            <div className="mt-8">{children}</div>
          </div>
        </section>
      </div>
    </main>
  );
}

