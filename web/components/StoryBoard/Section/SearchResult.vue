<template>
  <div class="relative">
    <!-- 左箭頭 -->
    <button
      v-if="!isLeftEnd"
      @click="scrollLeft"
      class="absolute top-1/2 left-0 transform -translate-y-1/2 z-10 p-2 bg-gray-500 text-white rounded-full opacity-80 0 hover:opacity-100"
    >
      &#8592;
    </button>

    <!-- 主要滾動區域 -->
    <div
      v-if="searchResult && searchResult.data.length"
      class="flex gap-3 overflow-x-auto hide-scrollbar"
      ref="scrollContainer"
    >
      <ClientOnly>
        <IBlurReveal
          v-for="(result, index) in searchResult.data"
          :key="result.title"
          :delay="0.2 * index"
          :duration="0.75"
        >
          <div
            class="relative cursor-pointer min-w-250px overflow-hidden rounded-xl border border-gray-950/[.1] bg-gray-950/[.01] p-4 hover:bg-gray-950/[.05] dark:border-gray-50/[.1] dark:bg-gray-50/[.10] dark:hover:bg-gray-50/[.15]"
          >
            <div class="flex flex-col">
              <h3 class="text-sm font-medium dark:text-white">
                {{ result.title }}
              </h3>
              <p
                class="text-xs font-medium text-gray-600 dark:text-gray-400 mt-1"
              >
                {{ result.description }}
              </p>
            </div>
          </div>
        </IBlurReveal>
      </ClientOnly>
    </div>

    <!-- 右箭頭 -->
    <button
      v-if="!isRightEnd"
      @click="scrollRight"
      class="absolute top-1/2 right-0 transform -translate-y-1/2 z-10 p-2 bg-gray-500 text-white rounded-full opacity-80 hover:opacity-100"
    >
      &#8594;
    </button>
  </div>
</template>

<script lang="ts" setup>
import { ref, computed } from "vue";
import { useScroll, useElementSize } from "@vueuse/core";
import type { SearchResult } from "~/type/ChatMessage.type";

const searchResult = defineModel<SearchResult>();
const scrollContainer = ref<HTMLElement | null>(null);

const { x } = useScroll(scrollContainer);

const { width: containerWidth } = useElementSize(scrollContainer);

const isLeftEnd = computed(() => {
  return x.value === 0;
});

const isRightEnd = computed(() => {
  console.log(
    x.value,
    containerWidth.value,
    scrollContainer.value?.scrollWidth
  );
  return (
    x.value + containerWidth.value + 1 >=
    (scrollContainer.value?.scrollWidth || 0)
  );
});

const scrollLeft = () => {
  if (scrollContainer.value) {
    scrollContainer.value.scrollBy({ left: -200, behavior: "smooth" });
  }
};

const scrollRight = () => {
  if (scrollContainer.value) {
    scrollContainer.value.scrollBy({ left: 200, behavior: "smooth" });
  }
};
</script>

<style scoped>
.hide-scrollbar::-webkit-scrollbar {
  display: none;
}

button {
  cursor: pointer;
}

button:hover {
  background-color: #4b5563; /* 可根据需要修改颜色 */
}

/* 适应不同屏幕 */
@media (max-width: 640px) {
  .min-w-250px {
    min-width: 180px;
  }
}
</style>
