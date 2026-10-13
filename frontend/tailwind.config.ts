import type { Config } from "tailwindcss";
import { BRAND, RISK } from "./lib/ui";

export default {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        canvas: "#faf9f6",
        surface: "#ffffff",
        sunken: "#f3f1ec",
        // Every step clears WCAG AA (4.5:1) on canvas/surface/sunken
        ink: {
          DEFAULT: "#20231f", // 15.1:1
          2: "#5e625b",       //  5.9:1
          3: "#6b6f68",       //  4.9:1 (4.5 on sunken)
        },
        line: {
          DEFAULT: "#e7e5df",
          strong: "#d9d6ce",
        },
        brand: {
          DEFAULT: BRAND,
          accent: "#435340", // hover/pressed
          deep: "#1f2a1d",   // dark editorial panels
          soft: "#eef1ea",
        },
        // Secondary accents: decoration and category, never risk
        slate: "#5a6b8a",
        ochre: { DEFAULT: "#c3a779", soft: "#f4ecdd" },
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
        serif: ["var(--font-serif)", "Georgia", "serif"],
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
        // Warm, low elevation, paired with a hairline border
        xs: "0 1px 2px rgba(32,35,31,0.05)",
        soft: "0 1px 2px rgba(32,35,31,0.04), 0 1px 3px rgba(32,35,31,0.03)",
        raised: "0 2px 4px -1px rgba(32,35,31,0.05), 0 10px 22px -8px rgba(32,35,31,0.10)",
        lift: "0 12px 32px -12px rgba(32,35,31,0.16), 0 24px 60px -24px rgba(32,35,31,0.14)",
        brand: "0 4px 12px -4px rgba(79,97,73,0.40)",
      },
      maxWidth: {
        content: "1120px",
      },
      transitionTimingFunction: {
        smooth: "cubic-bezier(0.22, 1, 0.36, 1)",
      },
      keyframes: {
        // CSS, not framer: plays before hydration, so the hero is never stuck hidden
        rise: {
          "0%": { opacity: "0", transform: "translateY(12px)" },
          "100%": { opacity: "1", transform: "none" },
        },
        shimmer: {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
      },
      animation: {
        shimmer: "shimmer 2.2s linear infinite",
        rise: "rise 0.6s cubic-bezier(0.22, 1, 0.36, 1) both",
      },
    },
  },
  plugins: [],
} satisfies Config;
