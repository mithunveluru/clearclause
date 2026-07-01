import type { Config } from "tailwindcss";

export default {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        canvas: "#fafbff",
        surface: "#ffffff",
        ink: {
          DEFAULT: "#0f172a",
          2: "#64748b",
          3: "#94a3b8",
        },
        line: {
          DEFAULT: "#e8ecf5",
          strong: "#dde4f0",
        },
        brand: {
          DEFAULT: "#4f46e5",
          accent: "#6366f1",
          deep: "#312e81",
          soft: "#eef2ff",
        },
        accent: "#4f46e5",
        risk: {
          low: "#16a34a",
          moderate: "#d97706",
          high: "#dc2626",
          critical: "#991b1b",
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
        // Cool, indigo-tinted elevation paired with a hairline border.
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
