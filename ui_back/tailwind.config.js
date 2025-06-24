/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        saffron: {
          50: '#fef7ed',
          100: '#fdefd4',
          200: '#fbdba8',
          300: '#f8c171',
          400: '#f49f38',
          500: '#f28b12',
          600: '#e37308',
          700: '#bc5209',
          800: '#96420f',
          900: '#793710',
          950: '#411a06',
        },
        terracotta: {
          50: '#fef2f2',
          100: '#fee2e2',
          200: '#fecaca',
          300: '#fca5a5',
          400: '#f87171',
          500: '#ef4444',
          600: '#dc2626',
          700: '#b91c1c',
          800: '#991b1b',
          900: '#7f1d1d',
          950: '#450a0a',
        },
        gold: {
          50: '#fffbeb',
          100: '#fef3c7',
          200: '#fde68a',
          300: '#fcd34d',
          400: '#fbbf24',
          500: '#f59e0b',
          600: '#d97706',
          700: '#b45309',
          800: '#92400e',
          900: '#78350f',
          950: '#451a03',
        },
        cream: {
          50: '#fefdfb',
          100: '#fefcf6',
          200: '#fdf8ed',
          300: '#fcf3e0',
          400: '#f9ebc8',
          500: '#f5dfa3',
          600: '#ead185',
          700: '#d4b158',
          800: '#b8943a',
          900: '#987a30',
          950: '#54421a',
        }
      },
      fontFamily: {
        'sanskrit': ['Noto Sans Devanagari', 'serif'],
        'heading': ['Inter', 'system-ui', 'sans-serif'],
        'body': ['system-ui', '-apple-system', 'sans-serif'],
      },
      animation: {
        'lotus-spin': 'spin 20s linear infinite',
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
    },
  },
  plugins: [],
};