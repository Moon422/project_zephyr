export default {
    plugins: {
        "@tailwindcss/postcss": {
            content: [
                './templates/**/*.html',
                './**/templates/**/*.html',
                './static/js/**/*.js',
            ]
        },
    }
}