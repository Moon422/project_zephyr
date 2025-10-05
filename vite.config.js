import { defineConfig } from 'vite';
import { resolve } from 'path';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
    build: {
        outDir: 'static/dist',
        rollupOptions: {
            input: {
                main: resolve(__dirname, 'static/src/main.js'),
            },
            output: {
                entryFileNames: 'js/[name].js',
            }
        },
    },
    plugins: [tailwindcss(),],
});
