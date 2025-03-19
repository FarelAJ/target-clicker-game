/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./src/**/*.{js,jsx,ts,tsx}",
        "./index.html",
    ],
    theme: {
        extend: {
            colors: {
                'game-primary': '#4F46E5',
                'game-secondary': '#10B981',
            }
        },
    },
    plugins: [],
}