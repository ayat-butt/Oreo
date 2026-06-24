import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // Brand (Taleemabad / Orenda)
        brand: {
          green: "#6aa84f",          // tree-logo green — accent / success
          "green-strong": "#3f7d33", // darker green for white-text CTAs (AA contrast)
          "green-soft": "#eef5ea",   // tint surface
          blue: "#3d85c6",           // info — "Draft" / "Pilot"
          "blue-strong": "#2f6aa0",
          "blue-soft": "#eaf2fa",
        },
        warning: "#b45309",
        danger: "#dc2626",
        "danger-soft": "#fef2f2",
      },
      fontFamily: {
        sans: ["var(--font-lato)", "system-ui", "sans-serif"],
        serif: ["var(--font-eb-garamond)", "Georgia", "serif"],
      },
      borderRadius: {
        xl: "0.75rem",
        "2xl": "1rem",
        "3xl": "1.5rem",
      },
      boxShadow: {
        // Soft, layered elevation scale (Stripe/Linear feel)
        xs: "0 1px 2px 0 rgb(15 23 42 / 0.04)",
        sm: "0 1px 3px 0 rgb(15 23 42 / 0.06), 0 1px 2px -1px rgb(15 23 42 / 0.05)",
        card: "0 1px 3px 0 rgb(15 23 42 / 0.05), 0 1px 2px -1px rgb(15 23 42 / 0.04)",
        md: "0 4px 12px -2px rgb(15 23 42 / 0.08), 0 2px 6px -2px rgb(15 23 42 / 0.05)",
        lg: "0 12px 28px -8px rgb(15 23 42 / 0.12), 0 4px 10px -6px rgb(15 23 42 / 0.06)",
        xl: "0 24px 48px -16px rgb(15 23 42 / 0.20), 0 8px 16px -8px rgb(15 23 42 / 0.08)",
        hover: "0 10px 28px -10px rgb(15 23 42 / 0.18)",
        pop: "0 24px 48px -16px rgb(15 23 42 / 0.22)",
        ring: "0 0 0 4px rgb(106 168 79 / 0.12)",
      },
      keyframes: {
        shimmer: { "100%": { transform: "translateX(100%)" } },
        "fade-up": {
          "0%": { opacity: "0", transform: "translateY(6px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
      },
      animation: {
        shimmer: "shimmer 1.6s infinite",
        "fade-up": "fade-up 0.35s ease-out both",
      },
    },
  },
  plugins: [],
};
export default config;
