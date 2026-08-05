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
          bg: "#0B0D12",
          surface: "#121722",
          "surface-raised": "#191F2C",
          text: "#F4F7FB",
          "text-muted": "#AAB4C3",
          border: "#2A3445",
          primary: "#FF7A66",
          "primary-hover": "#FF927F",
          "primary-active": "#E86250",
          focus: "#7DD3FC",
          success: "#43D19E",
          warning: "#F7C35F",
          danger: "#FF6B6B",
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
        focus: "0 0 0 3px rgb(125 211 252 / .45)",
      },
    },
  },
  plugins: [],
};

export default config;
