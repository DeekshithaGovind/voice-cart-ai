"use client";

import { createContext, useCallback, useContext, useEffect, useRef, useState } from "react";
import { WS_URL } from "./api";

export interface DashboardEvent {
  type: string;
  [key: string]: unknown;
}

interface DashboardContextValue {
  connected: boolean;
  lastEvent: DashboardEvent | null;
  subscribe: (handler: (event: DashboardEvent) => void) => () => void;
}

const DashboardContext = createContext<DashboardContextValue>({
  connected: false,
  lastEvent: null,
  subscribe: () => () => {},
});

export function DashboardProvider({ children }: { children: React.ReactNode }) {
  const [connected, setConnected] = useState(false);
  const [lastEvent, setLastEvent] = useState<DashboardEvent | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const handlersRef = useRef<Set<(event: DashboardEvent) => void>>(new Set());

  const subscribe = useCallback((handler: (event: DashboardEvent) => void) => {
    handlersRef.current.add(handler);
    return () => handlersRef.current.delete(handler);
  }, []);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;
    const ws = new WebSocket(`${WS_URL}/api/v1/ws/dashboard`);
    ws.onopen = () => setConnected(true);
    ws.onclose = () => {
      setConnected(false);
      setTimeout(connect, 3000);
    };
    ws.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data) as DashboardEvent;
        setLastEvent(data);
        handlersRef.current.forEach((h) => h(data));
      } catch {}
    };
    wsRef.current = ws;
  }, []);

  useEffect(() => {
    connect();
    return () => wsRef.current?.close();
  }, [connect]);

  return (
    <DashboardContext.Provider value={{ connected, lastEvent, subscribe }}>
      {children}
    </DashboardContext.Provider>
  );
}

export function useDashboard() {
  return useContext(DashboardContext);
}

/** Refresh data when orders/stages update */
export function useDashboardRefresh(onRefresh: () => void) {
  const { subscribe } = useDashboard();

  useEffect(() => {
    return subscribe((event) => {
      if (
        event.type === "order_confirmed" ||
        event.type === "stage_update" ||
        event.type === "dashboard_refresh"
      ) {
        onRefresh();
      }
    });
  }, [subscribe, onRefresh]);
}
