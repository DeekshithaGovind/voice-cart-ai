export interface ValidationDetailsData {
  product_matches?: Array<{
    raw_text: string;
    product_name: string | null;
    matched: boolean;
    confidence: number;
    nlu_tier: number;
    quantity: number;
  }>;
  quantity_validation?: Array<{
    product_name: string;
    requested: number;
    min_qty: number | null;
    passed: boolean;
    message?: string | null;
  }>;
  stock_validation?: Array<{
    product_name: string;
    requested: number;
    stock: number | null;
    passed: boolean;
    message?: string | null;
  }>;
  confirmation_status?: string;
  valid?: boolean;
  issues?: Array<{ code: string; message: string }>;
}

interface ValidationDetailsProps {
  details: ValidationDetailsData | null | undefined;
  compact?: boolean;
}

function StatusDot({ ok }: { ok: boolean }) {
  return (
    <span className={`inline-block h-2 w-2 rounded-full ${ok ? "bg-success" : "bg-danger"}`} />
  );
}

export function ValidationDetails({ details, compact }: ValidationDetailsProps) {
  if (!details) return null;

  const confirmStatus = details.confirmation_status || "pending";
  const confirmColor =
    confirmStatus === "confirmed" ? "text-success" : confirmStatus === "failed" ? "text-danger" : "text-warning";

  return (
    <div className={`space-y-3 ${compact ? "text-xs" : "text-sm"}`}>
      <div>
        <p className="mb-1.5 text-[10px] uppercase tracking-wider text-gray-500">Product Match Result</p>
        <div className="space-y-1">
          {(details.product_matches || []).map((m, i) => (
            <div key={i} className="flex items-center justify-between rounded-lg bg-surface-card/50 px-2 py-1">
              <span className="text-gray-300 truncate max-w-[60%]">{m.raw_text}</span>
              <span className="flex items-center gap-1.5 text-gray-400">
                <StatusDot ok={m.matched} />
                {m.matched ? m.product_name : "No match"}
              </span>
            </div>
          ))}
        </div>
      </div>

      <div>
        <p className="mb-1.5 text-[10px] uppercase tracking-wider text-gray-500">Quantity Validation</p>
        <div className="space-y-1">
          {(details.quantity_validation || []).map((q, i) => (
            <div key={i} className="flex items-center justify-between rounded-lg bg-surface-card/50 px-2 py-1">
              <span className="text-gray-300">{q.product_name}</span>
              <span className="flex items-center gap-1.5 text-gray-400">
                <StatusDot ok={q.passed} />
                {q.requested}{q.min_qty != null ? ` / min ${q.min_qty}` : ""}
              </span>
            </div>
          ))}
        </div>
      </div>

      <div>
        <p className="mb-1.5 text-[10px] uppercase tracking-wider text-gray-500">Stock Validation</p>
        <div className="space-y-1">
          {(details.stock_validation || []).map((s, i) => (
            <div key={i} className="flex items-center justify-between rounded-lg bg-surface-card/50 px-2 py-1">
              <span className="text-gray-300">{s.product_name}</span>
              <span className="flex items-center gap-1.5 text-gray-400">
                <StatusDot ok={s.passed} />
                {s.requested}{s.stock != null ? ` / ${s.stock} avail` : ""}
              </span>
            </div>
          ))}
        </div>
      </div>

      <div className="flex items-center justify-between border-t border-surface-border pt-2">
        <span className="text-[10px] uppercase tracking-wider text-gray-500">Final Confirmation</span>
        <span className={`font-medium capitalize ${confirmColor}`}>{confirmStatus}</span>
      </div>
    </div>
  );
}
