import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // Brand (Taleemabad / Orenda) — green is the single saturated CTA accent
        brand: {
          green: "#6aa84f",          // tree-logo green — accent / success
          "green-strong": "#3f7d33", // darker green for white-text CTAs (AA contrast)
          "green-soft": "#eef5ea",   // tint surface
          blue: "#3d85c6",           // info — "Draft" / "Pilot"
          "blue-strong": "#2f6aa0",
          "blue-soft": "#eaf2fa",
        },
        // Warm-cream chrome (Pinterest-style) — quiet surfaces that recede behind content
        cream: {
          canvas: "#ffffff",
          soft: "#fbfbf9",   // page wash
          card: "#f6f6f3",   // card / tile / search fill
          deep: "#e9e9e3",   // secondary button fill
          deeper: "#dcdcd4", // pressed
        },
        // Warm neutral text ramp
        ink: "#1c1c19",      // headings — warm near-black (softer than pure #000)
        body: "#33332e",     // paragraph
        mute: "#62625b",     // metadata / secondary
        ash: "#91918c",      // placeholder / disabled
        stone: "#c8c8c1",    // least-emphasis / disabled border
        hairline: "#e3e3dd",        // 1px borders
        "hairline-soft": "#ededE7", // lighter inline divider
        warning: "#b45309",
        danger: "#dc2626",
        "danger-soft": "#fdf2f2",
      },
      fontFamily: {
        // All-sans system (Inter), per the Pinterest/Pin Sans spec — no serif anywhere
        sans: ["var(--font-inter)", "system-ui", "sans-serif"],
        serif: ["var(--font-inter)", "system-ui", "sans-serif"],
        display: ["var(--font-inter)", "system-ui", "sans-serif"],
      },
      letterSpacing: {
        tightest: "-0.04em", // ~ -1.2px on display headings (the brand-voice negative tracking)
      },
      borderRadius: {
        // Pinterest shape vocabulary: 16px dominant, 32px for big cards/modals, pill for chips
        xl: "1rem",    // 16px — buttons, inputs, cards (dominant)
        "2xl": "1rem", // 16px — alias
        "3xl": "2rem", // 32px — large cards, modals, login
      },
      boxShadow: {
        // Mostly flat (Pinterest content surfaces use hairlines, not shadows)
        xs: "0 1px 2px 0 rgb(28 28 25 / 0.04)",
        sm: "0 1px 2px 0 rgb(28 28 25 / 0.05)",
        card: "0 1px 2px 0 rgb(28 28 25 / 0.04)",
        md: "0 6px 16px -6px rgb(28 28 25 / 0.10)",
        lg: "0 12px 28px -10px rgb(28 28 25 / 0.14)",
        xl: "0 24px 48px -16px rgb(28 28 25 / 0.20)",
        hover: "0 10px 26px -12px rgb(28 28 25 / 0.16)",
        pop: "0 20px 48px -16px rgb(28 28 25 / 0.24)",
        nav: "0 1px 0 0 rgb(28 28 25 / 0.06)",
        ring: "0 0 0 4px rgb(106 168 79 / 0.15)",
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
