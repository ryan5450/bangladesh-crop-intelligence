/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: [
    "./src/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        dark: {
          bg: "#060907",
          surface: "#0c120e",
          card: "rgba(16, 26, 20, 0.6)",
          border: "rgba(34, 197, 94, 0.12)",
          glass: "rgba(255, 255, 255, 0.03)",
        },
        agri: {
          50: "#ecfdf5",
          100: "#d1fae5",
          200: "#a7f3d0",
          300: "#6ee7b7",
          400: "#34d399",
          500: "#10b981",
          600: "#059669",
          700: "#047857",
          800: "#065f46",
          900: "#064e3b",
          accent: "#22c55e",
          lime: "#84cc16",
        },
      },
      backgroundImage: {
        "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
        "radial-emerald": "radial-gradient(circle at 50% 0%, rgba(16, 185, 129, 0.15) 0%, rgba(6, 9, 7, 0) 70%)",
        "radial-glow": "radial-gradient(circle at 80% 20%, rgba(34, 197, 94, 0.1) 0%, transparent 60%)",
      },
      boxShadow: {
        "glass": "0 8px 32px 0 rgba(0, 0, 0, 0.37)",
        "glow": "0 0 25px -5px rgba(16, 185, 129, 0.3)",
        "glow-lg": "0 0 50px -10px rgba(16, 185, 129, 0.4)",
      },
      animation: {
        "pulse-slow": "pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "float": "float 6s ease-in-out infinite",
      },
      keyframes: {
        float: {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-8px)" },
        },
      },
    },
  },
  plugins: [],
};

