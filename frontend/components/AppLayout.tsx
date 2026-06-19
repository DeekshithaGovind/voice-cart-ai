"use client";

import { Sidebar } from "@/components/Sidebar";

export function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div className="ml-64 flex flex-1 flex-col">{children}</div>
    </div>
  );
}
