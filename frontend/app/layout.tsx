import type { Metadata } from "next";
import "./globals.css";
import { AppLayout } from "@/components/AppLayout";
import { DashboardProvider } from "@/lib/DashboardProvider";

export const metadata: Metadata = {
  title: "VoiceCart AI — Voice Order Dashboard",
  description: "24/7 voice order booking for supermarkets and distributors",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="h-full">
      <body className="min-h-screen bg-surface font-sans text-gray-100 antialiased">
        <DashboardProvider>
          <AppLayout>{children}</AppLayout>
        </DashboardProvider>
      </body>
    </html>
  );
}
