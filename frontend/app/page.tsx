"use client";

import { useCallback, useEffect, useState } from "react";
import { motion } from "framer-motion";
import { IndianRupee, Phone, Radio, ShoppingBag } from "lucide-react";
import { DashboardShell } from "@/components/DashboardShell";
import { StatCard } from "@/components/StatCard";
import { TopBar } from "@/components/TopBar";
import { CallSimulator } from "@/components/CallSimulator";
import { api, formatCurrency, formatTime, tierLabel, tierColor } from "@/lib/api";
import { useDashboard, useDashboardRefresh } from "@/lib/DashboardProvider";

interface Analytics {
  total_orders: number;
  total_revenue: number;
  total_calls: number;
  orders_today: number;
  calls_today: number;
  active_calls: number;
  tier1_rate: number;
}

interface Order {
  id: string;
  customer_name: string | null;
  total_amount: number;
  nlu_tier_used: number | null;
  created_at: string;
  status: string;
}

export default function OverviewPage() {
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [orders, setOrders] = useState<Order[]>([]);
  const { connected } = useDashboard();

  const load = useCallback(async () => {
    try {
      const [a, o] = await Promise.all([
        api<Analytics>("/analytics/summary"),
        api<Order[]>("/orders?limit=5"),
      ]);
      setAnalytics(a);
      setOrders(o);
    } catch {}
  }, []);

  useEffect(() => { load(); const t = setInterval(load, 15000); return () => clearInterval(t); }, [load]);
  useDashboardRefresh(load);

  return (
    <>
      <TopBar title="Overview" subtitle="Real-time voice commerce command center" wsConnected={connected} />
      <DashboardShell>
        <div className="grid gap-6 lg:grid-cols-4">
          <StatCard label="Orders Today" value={analytics?.orders_today ?? "—"} icon={ShoppingBag} accent="cyan" change={`${analytics?.total_orders ?? 0} total`} />
          <StatCard label="Revenue" value={analytics ? formatCurrency(analytics.total_revenue) : "—"} icon={IndianRupee} accent="green" />
          <StatCard label="Calls Today" value={analytics?.calls_today ?? "—"} icon={Phone} accent="amber" change={`${analytics?.active_calls ?? 0} active`} />
          <StatCard label="Tier 1 Match Rate" value={analytics ? `${Math.round(analytics.tier1_rate * 100)}%` : "—"} icon={Radio} accent="rose" />
        </div>

        <div className="mt-8 grid gap-6 lg:grid-cols-3">
          <div className="lg:col-span-2">
            <div className="glass rounded-2xl border p-6">
              <h3 className="font-display text-lg font-semibold text-white">Recent Orders</h3>
              <div className="mt-4 space-y-3">
                {orders.map((o, i) => (
                  <motion.div
                    key={o.id}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.05 }}
                    className="flex items-center justify-between rounded-xl border border-surface-border bg-surface-card/50 px-4 py-3 card-hover"
                  >
                    <div>
                      <p className="font-medium text-white">{o.customer_name || "Guest"}</p>
                      <p className="text-xs text-gray-500">{formatTime(o.created_at)} · {tierLabel(o.nlu_tier_used)}</p>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold text-accent">{formatCurrency(o.total_amount)}</p>
                      <p className={`text-xs ${tierColor(o.nlu_tier_used)}`}>{o.status}</p>
                    </div>
                  </motion.div>
                ))}
                {orders.length === 0 && (
                  <p className="py-8 text-center text-sm text-gray-500">No orders yet — use the call simulator to create one</p>
                )}
              </div>
            </div>
          </div>
          <CallSimulator />
        </div>
      </DashboardShell>
    </>
  );
}
