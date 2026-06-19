"use client";

import { Bell, Search, Wifi, WifiOff } from "lucide-react";

interface TopBarProps {
  title: string;
  subtitle?: string;
  wsConnected?: boolean;
  children?: React.ReactNode;
}

export function TopBar({ title, subtitle, wsConnected, children }: TopBarProps) {
  return (
    <header className="sticky top-0 z-30 flex items-center justify-between border-b border-surface-border bg-surface/80 px-8 py-4 backdrop-blur-xl">
      <div>
        <h2 className="font-display text-xl font-semibold text-white">{title}</h2>
        {subtitle && <p className="text-sm text-gray-500">{subtitle}</p>}
      </div>

      <div className="flex items-center gap-4">
        {children}
        <div className="relative hidden md:block">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-500" />
          <input
            type="search"
            placeholder="Search orders, customers..."
            className="w-64 rounded-xl border border-surface-border bg-surface-card py-2 pl-10 pr-4 text-sm text-gray-200 placeholder-gray-500 outline-none focus:border-accent/50"
          />
        </div>

        <div className="flex items-center gap-2 rounded-xl border border-surface-border bg-surface-card px-3 py-2 text-xs">
          {wsConnected ? (
            <>
              <Wifi className="h-3.5 w-3.5 text-success" />
              <span className="text-success">Live</span>
            </>
          ) : (
            <>
              <WifiOff className="h-3.5 w-3.5 text-warning" />
              <span className="text-warning">Reconnecting</span>
            </>
          )}
        </div>

        <button className="relative rounded-xl border border-surface-border bg-surface-card p-2.5 text-gray-400 hover:text-white">
          <Bell className="h-4 w-4" />
          <span className="absolute right-2 top-2 h-1.5 w-1.5 rounded-full bg-accent" />
        </button>
      </div>
    </header>
  );
}
