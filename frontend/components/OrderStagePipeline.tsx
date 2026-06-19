"use client";

import clsx from "clsx";
import { Check } from "lucide-react";

export const ORDER_STAGES = [
  { id: "call_started", label: "Call Started" },
  { id: "transcript_received", label: "Transcript Received" },
  { id: "product_match", label: "Product Match" },
  { id: "validation", label: "Validation" },
  { id: "confirmation", label: "Confirmation" },
  { id: "order_created", label: "Order Created" },
];

interface StageHistoryItem {
  stage: string;
  at?: string;
}

interface OrderStagePipelineProps {
  currentStage: string;
  stages?: StageHistoryItem[];
  compact?: boolean;
}

export function OrderStagePipeline({ currentStage, stages = [], compact }: OrderStagePipelineProps) {
  const completed = new Set(stages.map((s) => s.stage));
  completed.add(currentStage);
  const currentIdx = ORDER_STAGES.findIndex((s) => s.id === currentStage);

  return (
    <div className={clsx("flex items-center gap-1", compact ? "flex-wrap" : "overflow-x-auto pb-1")}>
      {ORDER_STAGES.map((stage, i) => {
        const done = completed.has(stage.id) && i <= currentIdx;
        const active = stage.id === currentStage;
        return (
          <div key={stage.id} className="flex items-center gap-1 shrink-0">
            <div
              className={clsx(
                "flex items-center gap-1 rounded-lg px-2 py-1 text-[10px] font-medium transition-all",
                done && !active && "bg-success/10 text-success",
                active && "bg-accent/20 text-accent ring-1 ring-accent/40",
                !done && !active && "bg-surface-card text-gray-500"
              )}
            >
              {done && <Check className="h-3 w-3" />}
              {stage.label}
            </div>
            {i < ORDER_STAGES.length - 1 && (
              <div className={clsx("h-px w-3", done ? "bg-success/40" : "bg-surface-border")} />
            )}
          </div>
        );
      })}
    </div>
  );
}
