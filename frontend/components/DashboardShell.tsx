"use client";

import { motion } from "framer-motion";

export function DashboardShell({ children }: { children: React.ReactNode }) {
  return (
    <motion.main
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="flex-1 overflow-auto p-8"
    >
      {children}
    </motion.main>
  );
}
