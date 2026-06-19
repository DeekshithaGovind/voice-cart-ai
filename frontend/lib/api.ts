export const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
export const WS_URL = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000";

export async function api<T>(path: string, options?: RequestInit): Promise<T> {
  const isForm = options?.body instanceof FormData;
  const res = await fetch(`${API_URL}/api/v1${path}`, {
    ...options,
    headers: isForm
      ? options?.headers
      : { "Content-Type": "application/json", ...options?.headers },
    cache: "no-store",
  });
  if (!res.ok) {
    const err = await res.text().catch(() => "");
    throw new Error(err || `API error: ${res.status}`);
  }
  return res.json();
}

export async function apiUpload<T>(path: string, formData: FormData): Promise<T> {
  return api<T>(path, { method: "POST", body: formData });
}

export function formatCurrency(n: number) {
  return new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(n);
}

export function formatTime(iso: string) {
  return new Date(iso).toLocaleString("en-IN", { hour: "2-digit", minute: "2-digit", day: "numeric", month: "short" });
}

export function tierLabel(tier: number | null) {
  if (tier === 1) return "Tier 1 · Fuzzy";
  if (tier === 2) return "Tier 2 · NER";
  if (tier === 3) return "Tier 3 · LLM";
  return "—";
}

export function tierColor(tier: number | null) {
  if (tier === 1) return "text-success";
  if (tier === 2) return "text-warning";
  if (tier === 3) return "text-danger";
  return "text-gray-400";
}
