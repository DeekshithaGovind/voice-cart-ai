"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Activity,
  BarChart3,
  Headphones,
  LayoutDashboard,
  Package,
  Phone,
  Radio,
  Settings,
  Users,
  Zap,
} from "lucide-react";
import clsx from "clsx";

const nav = [
  { href: "/", label: "Overview", icon: LayoutDashboard },
  { href: "/orders", label: "Live Orders", icon: Radio },
  { href: "/calls", label: "Call Logs", icon: Phone },
  { href: "/customers", label: "Customers", icon: Users },
  { href: "/products", label: "Products", icon: Package },
  { href: "/analytics", label: "Analytics", icon: BarChart3 },
  { href: "/monitoring", label: "Monitoring", icon: Activity },
  { href: "/settings", label: "Settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 z-40 flex h-screen w-64 flex-col border-r border-surface-border bg-surface-raised/95 backdrop-blur-xl">
      <div className="flex items-center gap-3 border-b border-surface-border px-6 py-5">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-accent/20 to-emerald-500/20 ring-1 ring-accent/30">
          <Headphones className="h-5 w-5 text-accent" />
        </div>
        <div>
          <h1 className="font-display text-lg font-bold tracking-tight gradient-text">VoiceCart AI</h1>
          <p className="text-[10px] uppercase tracking-widest text-gray-500">Voice Commerce</p>
        </div>
      </div>

      <nav className="flex-1 space-y-1 p-4">
        {nav.map(({ href, label, icon: Icon }) => {
          const active = pathname === href;
          return (
            <Link
              key={href}
              href={href}
              className={clsx(
                "group flex items-center gap-3 rounded-xl px-4 py-2.5 text-sm font-medium transition-all",
                active
                  ? "bg-accent/10 text-accent shadow-glow"
                  : "text-gray-400 hover:bg-surface-hover hover:text-gray-200"
              )}
            >
              <Icon className={clsx("h-4 w-4", active && "text-accent")} />
              {label}
              {href === "/orders" && (
                <span className="ml-auto live-dot" title="Live" />
              )}
            </Link>
          );
        })}
      </nav>

      <div className="border-t border-surface-border p-4">
        <div className="glass rounded-xl p-4">
          <div className="flex items-center gap-2 text-xs text-gray-400">
            <Zap className="h-3.5 w-3.5 text-accent" />
            CPU-only NLU cascade
          </div>
          <p className="mt-1 text-[11px] text-gray-500">Tier 1 → 2 → 3 fallback</p>
        </div>
      </div>
    </aside>
  );
}
