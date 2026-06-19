import clsx from "clsx";
import { LucideIcon } from "lucide-react";

interface StatCardProps {
  label: string;
  value: string | number;
  change?: string;
  icon: LucideIcon;
  accent?: "cyan" | "green" | "amber" | "rose";
}

const accents = {
  cyan: "from-cyan-500/20 to-cyan-500/5 text-accent border-cyan-500/20",
  green: "from-emerald-500/20 to-emerald-500/5 text-success border-emerald-500/20",
  amber: "from-amber-500/20 to-amber-500/5 text-warning border-amber-500/20",
  rose: "from-rose-500/20 to-rose-500/5 text-danger border-rose-500/20",
};

export function StatCard({ label, value, change, icon: Icon, accent = "cyan" }: StatCardProps) {
  return (
    <div className={clsx("glass card-hover rounded-2xl border p-5 bg-gradient-to-br", accents[accent])}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-wider text-gray-500">{label}</p>
          <p className="mt-2 font-display text-2xl font-bold text-white">{value}</p>
          {change && <p className="mt-1 text-xs text-gray-400">{change}</p>}
        </div>
        <div className="rounded-xl bg-white/5 p-2.5">
          <Icon className="h-5 w-5" />
        </div>
      </div>
    </div>
  );
}
