/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'do-blue': '#0080FF',
        'do-dark': '#031B4D',
      }
    },
  },
  plugins: [],
}
