import { MyPreset } from "./primevue.config";

// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: "2024-11-01",
  devtools: { enabled: true },
  app: {},
  modules: [
    "@nuxtjs/color-mode",
    "@pinia/nuxt",
    "@unocss/nuxt",
    "@nuxt/icon",
    "@primevue/nuxt-module",
    "@vueuse/motion/nuxt",
  ],
  css: ["@unocss/reset/tailwind-compat.css"],
  primevue: {
    options: {
      theme: {
        preset: MyPreset,
      },
    },
  },
  modulesDir: ["../node_modules"],
  nitro: {
    devProxy: {
      "/api": {
        target: "http://localhost:8000/api",
        changeOrigin: true,
        autoRewrite: true,
      },
    },
  },
});
