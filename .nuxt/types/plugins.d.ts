// Generated by Nuxt'
import type { Plugin } from '#app'

type Decorate<T extends Record<string, any>> = { [K in keyof T as K extends string ? `$${K}` : never]: T[K] }

type InjectionType<A extends Plugin> = A extends {default: Plugin<infer T>} ? Decorate<T> : unknown

type NuxtAppInjections = 
  InjectionType<typeof import("../../node_modules/.pnpm/@pinia+nuxt@0.9.0_magicast@0.3.5_pinia@2.3.0_typescript@5.7.2_vue@3.5.13_typescript@5.7.2___rollup@4.29.2/node_modules/@pinia/nuxt/dist/runtime/payload-plugin.js")> &
  InjectionType<typeof import("../../node_modules/.pnpm/nuxt@3.15.1_@parcel+watcher@2.5.0_@types+node@22.10.5_db0@0.2.1_ioredis@5.4.2_magicast@0.3.5__asn7ifsfoy3nqewgb2zfqacozy/node_modules/nuxt/dist/app/plugins/revive-payload.client.js")> &
  InjectionType<typeof import("../../node_modules/.pnpm/nuxt@3.15.1_@parcel+watcher@2.5.0_@types+node@22.10.5_db0@0.2.1_ioredis@5.4.2_magicast@0.3.5__asn7ifsfoy3nqewgb2zfqacozy/node_modules/nuxt/dist/head/runtime/plugins/unhead.js")> &
  InjectionType<typeof import("../../node_modules/.pnpm/nuxt@3.15.1_@parcel+watcher@2.5.0_@types+node@22.10.5_db0@0.2.1_ioredis@5.4.2_magicast@0.3.5__asn7ifsfoy3nqewgb2zfqacozy/node_modules/nuxt/dist/app/plugins/router.js")> &
  InjectionType<typeof import("../../node_modules/.pnpm/nuxt@3.15.1_@parcel+watcher@2.5.0_@types+node@22.10.5_db0@0.2.1_ioredis@5.4.2_magicast@0.3.5__asn7ifsfoy3nqewgb2zfqacozy/node_modules/nuxt/dist/app/plugins/payload.client.js")> &
  InjectionType<typeof import("../../node_modules/.pnpm/nuxt@3.15.1_@parcel+watcher@2.5.0_@types+node@22.10.5_db0@0.2.1_ioredis@5.4.2_magicast@0.3.5__asn7ifsfoy3nqewgb2zfqacozy/node_modules/nuxt/dist/app/plugins/navigation-repaint.client.js")> &
  InjectionType<typeof import("../../node_modules/.pnpm/nuxt@3.15.1_@parcel+watcher@2.5.0_@types+node@22.10.5_db0@0.2.1_ioredis@5.4.2_magicast@0.3.5__asn7ifsfoy3nqewgb2zfqacozy/node_modules/nuxt/dist/app/plugins/check-outdated-build.client.js")> &
  InjectionType<typeof import("../../node_modules/.pnpm/nuxt@3.15.1_@parcel+watcher@2.5.0_@types+node@22.10.5_db0@0.2.1_ioredis@5.4.2_magicast@0.3.5__asn7ifsfoy3nqewgb2zfqacozy/node_modules/nuxt/dist/app/plugins/revive-payload.server.js")> &
  InjectionType<typeof import("../../node_modules/.pnpm/nuxt@3.15.1_@parcel+watcher@2.5.0_@types+node@22.10.5_db0@0.2.1_ioredis@5.4.2_magicast@0.3.5__asn7ifsfoy3nqewgb2zfqacozy/node_modules/nuxt/dist/app/plugins/chunk-reload.client.js")> &
  InjectionType<typeof import("../../node_modules/.pnpm/@pinia+nuxt@0.9.0_magicast@0.3.5_pinia@2.3.0_typescript@5.7.2_vue@3.5.13_typescript@5.7.2___rollup@4.29.2/node_modules/@pinia/nuxt/dist/runtime/plugin.vue3.js")> &
  InjectionType<typeof import("../../node_modules/.pnpm/@nuxt+icon@1.10.3_magicast@0.3.5_rollup@4.29.2_vite@6.0.7_@types+node@22.10.5_jiti@2.4.2_ters_y2xotmqybatxsqk4wt5eontise/node_modules/@nuxt/icon/dist/runtime/plugin.js")> &
  InjectionType<typeof import("../../node_modules/.pnpm/@nuxtjs+color-mode@3.5.2_magicast@0.3.5_rollup@4.29.2/node_modules/@nuxtjs/color-mode/dist/runtime/plugin.server.js")> &
  InjectionType<typeof import("../../node_modules/.pnpm/@nuxtjs+color-mode@3.5.2_magicast@0.3.5_rollup@4.29.2/node_modules/@nuxtjs/color-mode/dist/runtime/plugin.client.js")>

declare module '#app' {
  interface NuxtApp extends NuxtAppInjections { }

  interface NuxtAppLiterals {
    pluginName: 'nuxt:revive-payload:client' | 'nuxt:head' | 'nuxt:router' | 'nuxt:payload' | 'nuxt:revive-payload:server' | 'nuxt:chunk-reload' | 'pinia' | 'nuxt:global-components' | '@nuxt/icon'
  }
}

declare module 'vue' {
  interface ComponentCustomProperties extends NuxtAppInjections { }
}

export { }
