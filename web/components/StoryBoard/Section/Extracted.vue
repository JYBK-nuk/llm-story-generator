<template>
  <div v-if="dataExtracted">
    <ClientOnly>
      <IBlurReveal :delay="0.2" :duration="0.75">
        <div class="flex justify-around gap-2">
          <div class="flex flex-col">
            <p class="text-sm opacity-50">類型</p>
            <p>{{ dataExtracted.data.genre }}</p>
          </div>
          <div class="flex flex-col">
            <p class="text-sm opacity-50">關鍵元素</p>
            <p>{{ dataExtracted.data.key_elements }}</p>
          </div>
          <div class="flex flex-col">
            <p class="text-sm opacity-50">語言</p>
            <p>{{ dataExtracted.data.language }}</p>
          </div>
          <div class="flex flex-col">
            <p class="text-sm opacity-50">語氣</p>
            <p>{{ dataExtracted.data.tone }}</p>
          </div>
          <div class="flex flex-col">
            <p class="text-sm opacity-50">主題</p>
            <p>{{ dataExtracted.data.theme }}</p>
          </div>
        </div>
      </IBlurReveal>
    </ClientOnly>
  </div>
</template>

<script lang="ts" setup>
import type { DataExtracted } from "~/type/ChatMessage.type";
const dataExtracted = defineModel<DataExtracted>();
</script>

<style></style>
