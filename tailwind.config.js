/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./core/**/*.py",
    "./farms/**/*.py",
    "./climate/**/*.py",
    "./market/**/*.py",
    "./planner/**/*.py",
  ],
  theme: {
    extend: {
      colors: {
        forest: {
          DEFAULT: "#104632",
          700: "#104632",
          800: "#0A3325",
          900: "#062B20",
          950: "#041B14",
        },
        leaf: {
          DEFAULT: "#8FCB62",
          soft: "#C5E78B",
        },
        cream: "#F1F5EC",
        muted: "#A8BDB0",
        risk: {
          low: "#8FCB62",
          medium: "#F2B441",
          high: "#E76A6A",
        },
        water: {
          DEFAULT: "#4FB7D9",
          soft: "#BDE4F1",
        },
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
        display: ['"Plus Jakarta Sans"', "Inter", "sans-serif"],
      },
      borderRadius: {
        "2xl": "1.125rem",
        "3xl": "1.5rem",
      },
    },
  },
  plugins: [],
};
