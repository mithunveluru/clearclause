import type { Metadata } from "next";
import { Inter, Newsreader } from "next/font/google";
import { MotionProvider } from "@/components/ui/MotionProvider";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

const serif = Newsreader({
  subsets: ["latin"],
  variable: "--font-serif",
  display: "swap",
});

export const metadata: Metadata = {
  title: "ClearClause — Understand the details that matter",
  description:
    "ClearClause identifies what kind of financial or property document you have, surfaces the clauses that carry risk, and shows the wording behind every finding.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={`${inter.variable} ${serif.variable}`}>
      <body className="min-h-screen"><MotionProvider>{children}</MotionProvider></body>
    </html>
  );
}
