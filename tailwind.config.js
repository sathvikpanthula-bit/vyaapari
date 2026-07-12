/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        poppins: ['Poppins', 'sans-serif'],
      },
      colors: {
        brand: {
          orange: '#F97316',
          green:  '#22C55E',
          blue:   '#2563EB',
          gray:   '#F8FAFC',
        },
      },
      borderRadius: {
        card:    '12px',
        'card-lg': '16px',
      },
      boxShadow: {
        card:       '0 2px 16px 0 rgba(0,0,0,0.07)',
        'card-hover': '0 6px 24px 0 rgba(0,0,0,0.12)',
      },
    },
  },
  plugins: [],
}