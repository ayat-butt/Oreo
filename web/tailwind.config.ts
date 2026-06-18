import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // Brand (Taleemabad / Orenda)
        brand: {
          green: "#6aa84f",        // tree-logo green — success / brand accent
          "green-strong": "#3f7d33", // darker green for white-text CTAs (AA contrast)
          blue: "#3d85c6",         // info — "Draft" / "Pilot"
          "blue-strong": "#2f6aa0",
        },
        // semantic
        warning: "#b45309",
        danger: "#dc2626",
      },
      fontFamily: {
        sans: ["var(--font-lato)", "system-ui", "sans-serif"],
        serif: ["var(--font-eb-garamond)", "Georgia", "serif"],
      },
      fontVariantNumeric: {
        tabular: "tabular-nums",
      },
      boxShadow: {
        card: "0 1px 2px 0 rgb(15 23 42 / 0.04), 0 1px 3px 0 rgb(15 23 42 / 0.06)",
        pop: "0 10px 25px -5px rgb(15 23 42 / 0.12)",
      },
    },
  },
  plugins: [],
};
export default config;
