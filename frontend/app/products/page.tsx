"use client";

import { useCallback, useEffect, useState } from "react";
import { DashboardShell } from "@/components/DashboardShell";
import { TopBar } from "@/components/TopBar";
import { api, formatCurrency } from "@/lib/api";
import { useDashboard, useDashboardRefresh } from "@/lib/DashboardProvider";

interface Product {
  id: string;
  sku: string;
  name: string;
  name_hi: string | null;
  name_ta: string | null;
  category: string;
  unit: string;
  price: number;
  stock: number;
  min_qty: number;
  aliases: string[];
}

export default function ProductsPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const { connected } = useDashboard();

  const load = useCallback(() => {
    api<Product[]>("/products").then(setProducts).catch(() => {});
  }, []);

  useEffect(() => { load(); }, [load]);
  useDashboardRefresh(load);

  return (
    <>
      <TopBar title="Products" subtitle="Catalog with multilingual aliases for NLU matching" wsConnected={connected} />
      <DashboardShell>
        <div className="glass overflow-hidden rounded-2xl border">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-surface-border bg-surface-card/50 text-left text-xs uppercase tracking-wider text-gray-500">
                <th className="px-6 py-4">Product</th>
                <th className="px-6 py-4">SKU</th>
                <th className="px-6 py-4">Category</th>
                <th className="px-6 py-4">Price</th>
                <th className="px-6 py-4">Stock</th>
                <th className="px-6 py-4">Min Qty</th>
                <th className="px-6 py-4">Aliases</th>
              </tr>
            </thead>
            <tbody>
              {products.map((p) => (
                <tr key={p.id} className="border-b border-surface-border/50 hover:bg-surface-hover/50">
                  <td className="px-6 py-4">
                    <p className="font-medium text-white">{p.name}</p>
                    <p className="text-xs text-gray-500">{p.name_hi} · {p.name_ta}</p>
                  </td>
                  <td className="px-6 py-4 font-mono text-xs text-gray-400">{p.sku}</td>
                  <td className="px-6 py-4 text-gray-400">{p.category}</td>
                  <td className="px-6 py-4 text-accent">{formatCurrency(p.price)}/{p.unit}</td>
                  <td className="px-6 py-4">
                    <span className={p.stock < 50 ? "text-warning" : "text-gray-300"}>{p.stock} {p.unit}</span>
                  </td>
                  <td className="px-6 py-4 text-gray-400">{p.min_qty}</td>
                  <td className="max-w-xs px-6 py-4">
                    <div className="flex flex-wrap gap-1">
                      {(p.aliases || []).slice(0, 4).map((a) => (
                        <span key={a} className="rounded-md bg-surface-border px-1.5 py-0.5 text-[10px] text-gray-400">{a}</span>
                      ))}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </DashboardShell>
    </>
  );
}
