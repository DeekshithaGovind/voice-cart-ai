"use client";

import { useCallback, useEffect, useState } from "react";
import { DashboardShell } from "@/components/DashboardShell";
import { TopBar } from "@/components/TopBar";
import { api, formatCurrency } from "@/lib/api";
import { useDashboard, useDashboardRefresh } from "@/lib/DashboardProvider";

interface Customer {
  id: string;
  name: string;
  phone: string;
  language: string;
  credit_limit: number;
  credit_used: number;
  call_count: number;
}

export default function CustomersPage() {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const { connected } = useDashboard();

  const load = useCallback(() => {
    api<Customer[]>("/customers").then(setCustomers).catch(() => {});
  }, []);

  useEffect(() => { load(); }, [load]);
  useDashboardRefresh(load);

  return (
    <>
      <TopBar title="Customers" subtitle="Repeat caller profiles with credit & preferences" wsConnected={connected} />
      <DashboardShell>
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {customers.map((c) => {
            const creditPct = Math.round((c.credit_used / c.credit_limit) * 100);
            return (
              <div key={c.id} className="glass card-hover rounded-2xl border p-5">
                <div className="flex items-center gap-3">
                  <div className="flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br from-accent/30 to-emerald-500/20 font-display text-lg font-bold text-white">
                    {c.name.charAt(0)}
                  </div>
                  <div>
                    <p className="font-semibold text-white">{c.name}</p>
                    <p className="text-xs text-gray-500">{c.phone} · {c.language}</p>
                  </div>
                </div>
                <div className="mt-4 space-y-2">
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-500">Credit used</span>
                    <span className="text-gray-300">{formatCurrency(c.credit_used)} / {formatCurrency(c.credit_limit)}</span>
                  </div>
                  <div className="h-1.5 overflow-hidden rounded-full bg-surface-border">
                    <div
                      className={`h-full rounded-full ${creditPct > 80 ? "bg-danger" : "bg-accent"}`}
                      style={{ width: `${Math.min(creditPct, 100)}%` }}
                    />
                  </div>
                  <p className="text-xs text-gray-500">{c.call_count} calls · Redis-cached profile</p>
                </div>
              </div>
            );
          })}
        </div>
      </DashboardShell>
    </>
  );
}
