import { defineConfig } from 'vite';
import { resolve } from 'path';

export default defineConfig({
    build: {
        outDir: 'static/dist',
        rollupOptions: {
            input: {
                main: resolve(__dirname, 'static/js/main.js'),
            },
            output: {
                entryFileNames: 'js/[name].js',
                assetFileNames: 'assets/[name].[ext]'
            }
        },
    },
});
