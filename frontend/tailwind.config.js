/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'market-up': '#ef5350',
        'market-down': '#26a69a',
        'alert-high': '#ff6b6b',
        'alert-medium': '#ffd93d',
        'alert-low': '#6bcf7f',
      },
    },
  },
  plugins: [],
}
