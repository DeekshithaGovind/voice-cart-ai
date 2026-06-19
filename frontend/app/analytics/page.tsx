"use client";

import { useCallback, useEffect, useState } from "react";
import {
  BarChart, Bar, LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, CartesianGrid,
} from "recharts";
import { DashboardShell } from "@/components/DashboardShell";
import { TopBar } from "@/components/TopBar";
import { StatCard } from "@/components/StatCard";
import { api, formatCurrency } from "@/lib/api";
import { useDashboard, useDashboardRefresh } from "@/lib/DashboardProvider";
import { BarChart3, IndianRupee, Layers, Phone } from "lucide-react";

interface Analytics {
  total_orders: number;
  total_revenue: number;
  total_calls: number;
  avg_order_value: number;
  tier1_rate: number;
  tier2_rate: number;
  tier3_rate: number;
  orders_today: number;
  calls_today: number;
}

interface Charts {
  top_products: Array<{ name: string; quantity: number; revenue: number }>;
  revenue_trend: Array<{ day: string; revenue: number }>;
  orders_by_day: Array<{ day: string; orders: number }>;
  nlu_tier_usage: Array<{ tier: string; count: number }>;
}

const COLORS = ["#34d399", "#fbbf24", "#f87171", "#22d3ee", "#a78bfa"];

const tooltipStyle = { background: "#151d2e", border: "1px solid #1e293b", borderRadius: 12 };

export default function AnalyticsPage() {
  const [data, setData] = useState<Analytics | null>(null);
  const [charts, setCharts] = useState<Charts | null>(null);
  const { connected } = useDashboard();

  const load = useCallback(async () => {
    try {
      const [summary, chartData] = await Promise.all([
        api<Analytics>("/analytics/summary"),
        api<Charts>("/analytics/charts"),
      ]);
      setData(summary);
      setCharts(chartData);
    } catch {}
  }, []);

  useEffect(() => { load(); }, [load]);
  useDashboardRefresh(load);

  return (
    <>
      <TopBar title="Analytics" subtitle="NLU tier performance and order metrics" wsConnected={connected} />
      <DashboardShell>
        <div className="grid gap-6 lg:grid-cols-4">
          <StatCard label="Avg Order Value" value={data ? formatCurrency(data.avg_order_value) : "—"} icon={IndianRupee} />
          <StatCard label="Total Calls" value={data?.total_calls ?? "—"} icon={Phone} accent="amber" />
          <StatCard label="Total Orders" value={data?.total_orders ?? "—"} icon={BarChart3} accent="green" />
          <StatCard label="Tier 1 Rate" value={data ? `${Math.round(data.tier1_rate * 100)}%` : "—"} icon={Layers} accent="rose" />
        </div>

        <div className="mt-8 grid gap-6 lg:grid-cols-2">
          <div className="glass rounded-2xl border p-6">
            <h3 className="font-display font-semibold text-white">Top Products</h3>
            <div className="mt-4 h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={charts?.top_products || []} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis type="number" stroke="#64748b" fontSize={11} />
                  <YAxis dataKey="name" type="category" width={100} stroke="#64748b" fontSize={10} />
                  <Tooltip contentStyle={tooltipStyle} />
                  <Bar dataKey="quantity" fill="#22d3ee" radius={[0, 4, 4, 0]} name="Qty" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="glass rounded-2xl border p-6">
            <h3 className="font-display font-semibold text-white">Revenue Trend</h3>
            <div className="mt-4 h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={charts?.revenue_trend || []}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="day" stroke="#64748b" fontSize={11} tickFormatter={(d) => d.slice(5)} />
                  <YAxis stroke="#64748b" fontSize={11} />
                  <Tooltip contentStyle={tooltipStyle} formatter={(v: number) => formatCurrency(v)} />
                  <Line type="monotone" dataKey="revenue" stroke="#34d399" strokeWidth={2} dot={{ fill: "#34d399" }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="glass rounded-2xl border p-6">
            <h3 className="font-display font-semibold text-white">Orders by Day</h3>
            <div className="mt-4 h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={charts?.orders_by_day || []}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="day" stroke="#64748b" fontSize={11} tickFormatter={(d) => d.slice(5)} />
                  <YAxis stroke="#64748b" fontSize={11} allowDecimals={false} />
                  <Tooltip contentStyle={tooltipStyle} />
                  <Bar dataKey="orders" fill="#a78bfa" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="glass rounded-2xl border p-6">
            <h3 className="font-display font-semibold text-white">NLU Tier Usage</h3>
            <div className="mt-4 h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={charts?.nlu_tier_usage || []}
                    dataKey="count"
                    nameKey="tier"
                    cx="50%"
                    cy="50%"
                    innerRadius={55}
                    outerRadius={85}
                    paddingAngle={3}
                  >
                    {(charts?.nlu_tier_usage || []).map((_, i) => (
                      <Cell key={i} fill={COLORS[i % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={tooltipStyle} />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="mt-2 flex flex-wrap justify-center gap-3 text-xs text-gray-400">
              {(charts?.nlu_tier_usage || []).map((t, i) => (
                <span key={t.tier} className="flex items-center gap-1">
                  <span className="h-2 w-2 rounded-full" style={{ background: COLORS[i] }} />
                  {t.tier}: {t.count}
                </span>
              ))}
            </div>
          </div>
        </div>
      </DashboardShell>
    </>
  );
}
