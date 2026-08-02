import type { Config } from "tailwindcss";
import { BRAND, RISK } from "./lib/ui";

export default {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        canvas: "#fafbff",
        surface: "#ffffff",
        // Every step clears WCAG AA (4.5:1) on canvas/surface
        ink: {
          DEFAULT: "#0f172a", // 16.8:1
          2: "#475569",       //  7.5:1
          3: "#5b6b80",       //  5.4:1 — 4.8:1 cleared white but missed on tinted surfaces
        },
        line: {
          DEFAULT: "#e8ecf5",
          strong: "#dde4f0",
        },
        brand: {
          DEFAULT: BRAND,
          accent: "#6366f1",
          deep: "#312e81",
          soft: "#eef2ff",
        },
        accent: BRAND,
        // Generated from lib/ui.ts RISK — the single source, with the contrast notes.
        // `text-risk-high` and `bg-risk-high-tint` are the same values severityMeta() returns.
        risk: {
          low: { DEFAULT: RISK.low.color, tint: RISK.low.tint },
          moderate: { DEFAULT: RISK.medium.color, tint: RISK.medium.tint },
          high: { DEFAULT: RISK.high.color, tint: RISK.high.tint },
          critical: { DEFAULT: RISK.critical.color, tint: RISK.critical.tint },
        },
      },
      fontFamily: {
        sans: ["var(--font-inter)", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "sans-serif"],
      },
      letterSpacing: {
        tight: "-0.02em",
        tighter: "-0.035em",
      },
      borderRadius: {
        lg: "10px",
        xl: "12px",
        "2xl": "16px",
        "3xl": "22px",
      },
      boxShadow: {
        // Indigo-tinted elevation, paired with a hairline border
        xs: "0 1px 2px rgba(15,23,42,0.05)",
        soft: "0 1px 2px rgba(15,23,42,0.04), 0 1px 3px rgba(15,23,42,0.03)",
        raised: "0 2px 4px -1px rgba(15,23,42,0.05), 0 10px 22px -8px rgba(30,27,75,0.12)",
        lift: "0 10px 30px -10px rgba(30,27,75,0.18), 0 18px 50px -20px rgba(30,27,75,0.16)",
        brand: "0 6px 18px -4px rgba(79,70,229,0.45)",
      },
      maxWidth: {
        content: "1080px",
      },
      transitionTimingFunction: {
        smooth: "cubic-bezier(0.22, 1, 0.36, 1)",
      },
      keyframes: {
        shimmer: {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
      },
      animation: {
        shimmer: "shimmer 2.2s linear infinite",
      },
    },
  },
  plugins: [],
} satisfies Config;
