"use client";

import { useCallback, useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { DashboardShell } from "@/components/DashboardShell";
import { TopBar } from "@/components/TopBar";
import { OrderStagePipeline } from "@/components/OrderStagePipeline";
import { ValidationDetails, ValidationDetailsData } from "@/components/ValidationDetails";
import { api, formatCurrency, formatTime, tierLabel, tierColor } from "@/lib/api";
import { useDashboard, useDashboardRefresh } from "@/lib/DashboardProvider";

interface OrderItem {
  product_name: string;
  quantity: number;
  line_total: number;
  nlu_tier: number;
}

interface Order {
  id: string;
  customer_name: string | null;
  customer_phone: string | null;
  total_amount: number;
  nlu_tier_used: number | null;
  language: string;
  created_at: string;
  status: string;
  items: OrderItem[];
}

interface ActiveSession {
  session_id: string;
  customer_name: string | null;
  phone: string;
  state: string;
  current_stage: string;
  stages: Array<{ stage: string; at?: string }>;
  transcript: string;
  validation_details?: ValidationDetailsData;
}

export default function LiveOrdersPage() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [activeSessions, setActiveSessions] = useState<ActiveSession[]>([]);
  const [flashId, setFlashId] = useState<string | null>(null);
  const [expandedSession, setExpandedSession] = useState<string | null>(null);
  const { connected, subscribe } = useDashboard();

  const load = useCallback(async () => {
    try {
      const [orderData, active] = await Promise.all([
        api<Order[]>("/orders?limit=30"),
        api<ActiveSession[]>("/calls/active"),
      ]);
      setOrders(orderData);
      setActiveSessions(active);
    } catch {}
  }, []);

  useEffect(() => { load(); }, [load]);

  useDashboardRefresh(load);

  useEffect(() => {
    return subscribe((event) => {
      if (event.type === "order_confirmed" && event.order_id) {
        setFlashId(String(event.order_id));
        setTimeout(() => setFlashId(null), 3000);
      }
      if (event.type === "stage_update") load();
    });
  }, [subscribe, load]);

  return (
    <>
      <TopBar title="Live Orders" subtitle="Real-time order board — updates via WebSocket" wsConnected={connected}>
        <div className="flex items-center gap-2 rounded-xl border border-success/30 bg-success/10 px-3 py-1.5 text-xs text-success">
          <span className="live-dot" /> Streaming
        </div>
      </TopBar>
      <DashboardShell>
        {activeSessions.length > 0 && (
          <div className="mb-6 space-y-3">
            <h3 className="font-display text-sm font-semibold text-white">Active Processing</h3>
            {activeSessions.map((s) => (
              <div key={s.session_id} className="glass rounded-2xl border border-accent/20 p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-white">{s.customer_name || s.phone}</p>
                    <p className="text-xs text-gray-500 truncate max-w-md">{s.transcript || "Listening…"}</p>
                  </div>
                  <button
                    onClick={() => setExpandedSession(expandedSession === s.session_id ? null : s.session_id)}
                    className="text-xs text-accent hover:underline"
                  >
                    {expandedSession === s.session_id ? "Hide" : "Details"}
                  </button>
                </div>
                <div className="mt-3">
                  <OrderStagePipeline currentStage={s.current_stage} stages={s.stages} />
                </div>
                {expandedSession === s.session_id && s.validation_details && (
                  <div className="mt-3 border-t border-surface-border pt-3">
                    <ValidationDetails details={s.validation_details} compact />
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          <AnimatePresence>
            {orders.map((order, i) => (
              <motion.div
                key={order.id}
                layout
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                transition={{ delay: i * 0.03 }}
                className={`glass card-hover rounded-2xl border p-5 ${
                  flashId === order.id ? "ring-2 ring-success shadow-glow" : ""
                }`}
              >
                <div className="flex items-start justify-between">
                  <div>
                    <p className="font-display text-lg font-semibold text-white">{order.customer_name}</p>
                    <p className="text-xs text-gray-500">{order.customer_phone} · {order.language.toUpperCase()}</p>
                  </div>
                  <span className="rounded-lg bg-success/10 px-2 py-1 text-xs font-medium text-success">{order.status}</span>
                </div>

                <div className="mt-3">
                  <OrderStagePipeline currentStage="order_created" stages={[
                    { stage: "call_started" }, { stage: "transcript_received" }, { stage: "product_match" },
                    { stage: "validation" }, { stage: "confirmation" }, { stage: "order_created" },
                  ]} compact />
                </div>

                <ul className="mt-4 space-y-2 border-t border-surface-border pt-4">
                  {order.items.map((item, j) => (
                    <li key={j} className="flex justify-between text-sm">
                      <span className="text-gray-300">{item.quantity}× {item.product_name}</span>
                      <span className="text-gray-500">{formatCurrency(item.line_total)}</span>
                    </li>
                  ))}
                </ul>

                <div className="mt-4 flex items-center justify-between border-t border-surface-border pt-4">
                  <div>
                    <p className="text-xs text-gray-500">{formatTime(order.created_at)}</p>
                    <p className={`text-xs ${tierColor(order.nlu_tier_used)}`}>{tierLabel(order.nlu_tier_used)}</p>
                  </div>
                  <p className="font-display text-xl font-bold text-accent">{formatCurrency(order.total_amount)}</p>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
        {orders.length === 0 && (
          <div className="flex flex-col items-center justify-center py-24 text-gray-500">
            <p className="text-lg">Waiting for live orders...</p>
            <p className="mt-2 text-sm">Use Overview → Call Simulator to place a demo order</p>
          </div>
        )}
      </DashboardShell>
    </>
  );
}
