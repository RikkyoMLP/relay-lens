import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";
import { DevTools } from "@vitejs/devtools";
import { VueTracer } from "vite-plugin-vue-tracer";
import UnoCSS from "unocss/vite";

const __dirname = dirname(fileURLToPath(import.meta.url));

const defaultProxySettings = {
  "/api": {
    target: "http://localhost:7860",
    changeOrigin: true,
  },
}

export default defineConfig({
  plugins: [vue(), DevTools(), VueTracer(), UnoCSS()],
  resolve: {
    alias: {
      "@": resolve(__dirname, "src"),
    },
  },
  server: {
    proxy: defaultProxySettings,
  },
  preview: {
    proxy: defaultProxySettings,
  },
  build: {
    chunkSizeWarningLimit: 1000,
  },
});
