/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./templates/**/*.html', './static/**/*.js'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: '#94413d',
        'primary-hover': '#b04e49',
        'background-light': '#f7f6f6',
        'background-dark': '#1d1515',
        'surface-dark': '#241f1e',
        'sidebar-dark': '#181414',
        'border-dark': '#342d2d',
        'text-muted': '#c4b5b3',
        'alert-red': '#ef4444',
      },
      fontFamily: {
        display: ['Space Grotesk', 'sans-serif'],
        sans: ['Space Grotesk', 'sans-serif'],
      },
      borderRadius: {
        DEFAULT: '0.5rem',
        lg: '1rem',
        xl: '1.5rem',
        '2xl': '2rem',
        full: '9999px',
      },
      boxShadow: {
        glow: '0 0 20px rgba(148, 65, 61, 0.4)',
        card: '0 10px 30px -5px rgba(0, 0, 0, 0.6)',
      },
      backgroundImage: {
        'poncho-pattern':
          "url(\"data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%2394413d' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E\")",
      },
    },
  },
  plugins: [require('@tailwindcss/forms'), require('@tailwindcss/container-queries')],
};
