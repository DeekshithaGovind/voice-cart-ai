"use client";

import { useState } from "react";
import { DashboardShell } from "@/components/DashboardShell";
import { TopBar } from "@/components/TopBar";
import { api } from "@/lib/api";

export default function SettingsPage() {
  const [learningResult, setLearningResult] = useState<string | null>(null);

  const runLearning = async () => {
    try {
      const res = await api<{ learned_aliases: number; processed_orders: number }>("/jobs/nightly-learning", { method: "POST" });
      setLearningResult(`Learned ${res.learned_aliases} aliases from ${res.processed_orders} order items`);
    } catch {
      setLearningResult("Failed to run learning job");
    }
  };

  return (
    <>
      <TopBar title="Settings" subtitle="System configuration and maintenance" />
      <DashboardShell>
        <div className="max-w-2xl space-y-6">
          <div className="glass rounded-2xl border p-6">
            <h3 className="font-display font-semibold text-white">NLU Configuration</h3>
            <dl className="mt-4 space-y-3 text-sm">
              <div className="flex justify-between border-b border-surface-border pb-2">
                <dt className="text-gray-500">Tier 1</dt>
                <dd className="text-gray-300">Keyword / Trie / Fuzzy (rapidfuzz)</dd>
              </div>
              <div className="flex justify-between border-b border-surface-border pb-2">
                <dt className="text-gray-500">Tier 2</dt>
                <dd className="text-gray-300">Synonym + NER (EN/HI/TA code-mix)</dd>
              </div>
              <div className="flex justify-between border-b border-surface-border pb-2">
                <dt className="text-gray-500">Tier 3</dt>
                <dd className="text-gray-300">Local LLM via Ollama (disabled by default)</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-gray-500">Languages</dt>
                <dd className="text-gray-300">English, Hindi, Tamil</dd>
              </div>
            </dl>
          </div>

          <div className="glass rounded-2xl border p-6">
            <h3 className="font-display font-semibold text-white">Validation Rules</h3>
            <ul className="mt-4 space-y-2 text-sm text-gray-400">
              <li>Stock availability check</li>
              <li>Minimum quantity per product</li>
              <li>Customer credit limit check</li>
              <li>Up to 2 clarification attempts before fail</li>
            </ul>
          </div>

          <div className="glass rounded-2xl border p-6">
            <h3 className="font-display font-semibold text-white">Nightly Learning</h3>
            <p className="mt-2 text-sm text-gray-500">Update product aliases from successful Tier 1 matches</p>
            <button
              onClick={runLearning}
              className="mt-4 rounded-xl bg-accent/20 px-4 py-2.5 text-sm font-medium text-accent ring-1 ring-accent/30 hover:bg-accent/30"
            >
              Run Learning Job Now
            </button>
            {learningResult && <p className="mt-3 text-sm text-success">{learningResult}</p>}
          </div>
        </div>
      </DashboardShell>
    </>
  );
}
