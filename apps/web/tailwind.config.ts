import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        clipmind: {
          bg: "#000000",
          surface: "#0A0A0A",
          "surface-raised": "#121212",
          text: "#EDEDED",
          "text-muted": "#A1A1AA",
          border: "rgba(255,255,255,0.08)",
          primary: "#FFFFFF",
          "primary-hover": "#E5E5E5",
          "primary-active": "#CCCCCC",
          focus: "rgba(255,255,255,0.2)",
          success: "#10B981",
          warning: "#F59E0B",
          danger: "#EF4444",
        },
      },
      fontFamily: {
        sans: [
          "Inter Display",
          "Inter",
          "ui-sans-serif",
          "system-ui",
          "sans-serif",
        ],
      },
      borderRadius: {
        sm: "8px",
        md: "12px",
        lg: "20px",
        pill: "999px",
      },
      boxShadow: {
        sm: "0 1px 2px rgb(0 0 0 / .28)",
        md: "0 12px 32px rgb(0 0 0 / .28)",
        focus: "0 0 0 3px rgba(255, 255, 255, 0.2)",
      },
    },
  },
  plugins: [],
};

export default config;
