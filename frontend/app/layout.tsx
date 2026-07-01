import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { MotionProvider } from "@/components/ui/MotionProvider";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

export const metadata: Metadata = {
  title: "ClearClause — Understand what you're agreeing to",
  description:
    "ClearClause reviews loan agreements and subscription terms for hidden fees, penalties, and auto-renew traps — in plain English.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={inter.variable}>
      <body className="min-h-screen"><MotionProvider>{children}</MotionProvider></body>
    </html>
  );
}
