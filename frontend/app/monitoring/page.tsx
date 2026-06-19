"use client";

import { useCallback, useEffect, useState } from "react";
import { DashboardShell } from "@/components/DashboardShell";
import { TopBar } from "@/components/TopBar";
import { StatCard } from "@/components/StatCard";
import { api, formatTime } from "@/lib/api";
import { useDashboard, useDashboardRefresh } from "@/lib/DashboardProvider";
import { CheckCircle, AlertTriangle, XCircle, Database, Server, Radio, Users, ShoppingBag, Phone } from "lucide-react";

interface Monitoring {
  api: string;
  backend: string;
  database: string;
  redis: string;
  websocket_connections: number;
  active_sessions: number;
  active_calls: number;
  total_orders: number;
  total_customers: number;
  last_order_at: string | null;
  uptime_hint: string;
}

function StatusBadge({ status }: { status: string }) {
  const ok = status === "ok";
  const degraded = status === "degraded";
  const Icon = ok ? CheckCircle : degraded ? AlertTriangle : XCircle;
  const color = ok ? "text-success" : degraded ? "text-warning" : "text-danger";
  return (
    <span className={`flex items-center gap-2 ${color}`}>
      <Icon className="h-4 w-4" />
      {status}
    </span>
  );
}

export default function MonitoringPage() {
  const [status, setStatus] = useState<Monitoring | null>(null);
  const { connected } = useDashboard();

  const load = useCallback(() => {
    api<Monitoring>("/monitoring/status").then(setStatus).catch(() => {});
  }, []);

  useEffect(() => {
    load();
    const t = setInterval(load, 5000);
    return () => clearInterval(t);
  }, [load]);

  useDashboardRefresh(load);

  const services = status
    ? [
        { name: "Database Status", status: status.database, icon: Database },
        { name: "Redis Status", status: status.redis, icon: Server },
        { name: "Backend Status", status: status.backend, icon: Radio },
      ]
    : [];

  return (
    <>
      <TopBar title="Monitoring" subtitle="System health and live session metrics" wsConnected={connected} />
      <DashboardShell>
        <div className="grid gap-6 md:grid-cols-3">
          {services.map((s) => (
            <div key={s.name} className="glass card-hover rounded-2xl border p-6">
              <div className="flex items-center gap-2 text-sm text-gray-500">
                <s.icon className="h-4 w-4" />
                {s.name}
              </div>
              <p className="mt-2 font-display text-2xl"><StatusBadge status={s.status} /></p>
            </div>
          ))}
        </div>

        <div className="mt-8 grid gap-6 lg:grid-cols-4">
          <StatCard label="Active Calls" value={status?.active_calls ?? "—"} icon={Phone} accent="cyan" />
          <StatCard label="Total Orders" value={status?.total_orders ?? "—"} icon={ShoppingBag} accent="green" />
          <StatCard label="Total Customers" value={status?.total_customers ?? "—"} icon={Users} accent="amber" />
          <StatCard label="WebSocket Clients" value={status?.websocket_connections ?? "—"} icon={Radio} accent="rose" />
        </div>

        <div className="mt-8 grid gap-6 md:grid-cols-2">
          <div className="glass rounded-2xl border p-6">
            <h3 className="font-display font-semibold text-white">Live Metrics</h3>
            <dl className="mt-4 space-y-3 text-sm">
              <div className="flex justify-between">
                <dt className="text-gray-500">API status</dt>
                <dd><StatusBadge status={status?.api || "unknown"} /></dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-500">Active call sessions</dt>
                <dd className="font-mono text-accent">{status?.active_sessions ?? 0}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-500">Last order</dt>
                <dd className="text-gray-300">{status?.last_order_at ? formatTime(status.last_order_at) : "—"}</dd>
              </div>
            </dl>
          </div>

          <div className="glass rounded-2xl border p-6">
            <h3 className="font-display font-semibold text-white">Pipeline</h3>
            <ul className="mt-4 space-y-2 text-sm text-gray-400">
              <li>→ faster-whisper STT (CPU) → NLU cascade</li>
              <li>→ Redis Streams (order events)</li>
              <li>→ Parallel: DB write · notification · ERP webhook · dashboard WS</li>
              <li>→ Nightly learning job updates aliases</li>
            </ul>
            <p className="mt-4 text-xs text-gray-500">{status?.uptime_hint}</p>
          </div>
        </div>
      </DashboardShell>
    </>
  );
}
