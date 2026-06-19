"use client";

import { useCallback, useEffect, useState } from "react";
import { DashboardShell } from "@/components/DashboardShell";
import { TopBar } from "@/components/TopBar";
import { api, formatTime } from "@/lib/api";
import { useDashboard, useDashboardRefresh } from "@/lib/DashboardProvider";

interface CallLog {
  id: string;
  phone: string;
  customer_name: string | null;
  status: string;
  language: string;
  duration_sec: number;
  transcript: string | null;
  clarification_count: number;
  started_at: string;
}

const statusColors: Record<string, string> = {
  completed: "text-success bg-success/10",
  clarifying: "text-warning bg-warning/10",
  failed: "text-danger bg-danger/10",
  started: "text-accent bg-accent/10",
};

export default function CallLogsPage() {
  const [calls, setCalls] = useState<CallLog[]>([]);
  const { connected } = useDashboard();

  const load = useCallback(() => {
    api<CallLog[]>("/calls?limit=50").then(setCalls).catch(() => {});
  }, []);

  useEffect(() => { load(); }, [load]);
  useDashboardRefresh(load);

  return (
    <>
      <TopBar title="Call Logs" subtitle="Inbound voice session history" wsConnected={connected} />
      <DashboardShell>
        <div className="glass overflow-hidden rounded-2xl border">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-surface-border bg-surface-card/50 text-left text-xs uppercase tracking-wider text-gray-500">
                <th className="px-6 py-4">Caller</th>
                <th className="px-6 py-4">Status</th>
                <th className="px-6 py-4">Language</th>
                <th className="px-6 py-4">Transcript</th>
                <th className="px-6 py-4">Clarifications</th>
                <th className="px-6 py-4">Time</th>
              </tr>
            </thead>
            <tbody>
              {calls.map((c) => (
                <tr key={c.id} className="border-b border-surface-border/50 hover:bg-surface-hover/50">
                  <td className="px-6 py-4">
                    <p className="font-medium text-white">{c.customer_name || "Unknown"}</p>
                    <p className="text-xs text-gray-500">{c.phone}</p>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`rounded-lg px-2 py-1 text-xs font-medium ${statusColors[c.status] || "text-gray-400"}`}>
                      {c.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-gray-400">{c.language}</td>
                  <td className="max-w-xs truncate px-6 py-4 text-gray-400">{c.transcript || "—"}</td>
                  <td className="px-6 py-4 text-gray-400">{c.clarification_count}</td>
                  <td className="px-6 py-4 text-gray-500">{formatTime(c.started_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {calls.length === 0 && <p className="py-12 text-center text-gray-500">No call logs yet</p>}
        </div>
      </DashboardShell>
    </>
  );
}
