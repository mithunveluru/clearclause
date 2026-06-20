import type { Config } from "tailwindcss";

export default {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./lib/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        canvas: "#fafafa",
        surface: "#ffffff",
        ink: {
          DEFAULT: "#191919",
          2: "#5f5f63",
          3: "#9a9aa0",
        },
        line: {
          DEFAULT: "#ececef",
          strong: "#e0e0e4",
        },
        accent: "#0a5dd6",
        risk: {
          low: "#1a7f5a",
          moderate: "#b2670a",
          high: "#c0362c",
          critical: "#7c1d12",
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
        "3xl": "20px",
      },
      boxShadow: {
        // Elevation system: paired with a hairline border, kept whisper-soft.
        xs: "0 1px 2px rgba(16,24,40,0.04)",
        soft: "0 1px 2px rgba(16,24,40,0.04), 0 1px 3px rgba(16,24,40,0.02)",
        raised: "0 2px 4px -1px rgba(16,24,40,0.05), 0 8px 16px -6px rgba(16,24,40,0.08)",
        lift: "0 8px 24px -8px rgba(16,24,40,0.12), 0 16px 48px -16px rgba(16,24,40,0.12)",
      },
      maxWidth: {
        content: "1080px",
      },
      transitionTimingFunction: {
        smooth: "cubic-bezier(0.22, 1, 0.36, 1)",
      },
    },
  },
  plugins: [],
} satisfies Config;
