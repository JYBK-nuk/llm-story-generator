<template>
  <div v-if="storyResult" class="flex flex-col gap-3">
    <div class="font-bold text-3xl text-center">
      {{ storyResult.data.title }}
    </div>
    <div class="container" v-auto-animate>
      <div class="p-4 float-left" v-if="storyResult.data.image">
        <ClientOnly>
          <IBlurReveal :delay="0.2" :duration="0.75">
            <StoryBoardSectionImage
              class="shadow-sm rounded-lg overflow-hidden"
              :url="storyResult.data.image"
              :prompt="storyResult.data.image_prompt"
            />
          </IBlurReveal>
        </ClientOnly>
      </div>
      <p
        contenteditable="true"
        style="white-space: pre-wrap"
        class="focus-visible:outline-none"
        @input="onContentChange"
      >
        {{ storyResult.data.content }}
      </p>
      <div class="flex flex-row gap-4 mt-8" v-if="storyResult.data.evaluation_score">
        <div class="w-1/4 p-4  border border-gray-950/[.1] bg-gray-950/[.01] p-4 hover:bg-gray-950/[.05] dark:border-gray-50/[.1] dark:bg-gray-50/[.10] dark:hover:bg-gray-50/[.15] shadow-md rounded-lg text-center">
          <h3 class="text-xl font-semibold text-gray-700">BLEU</h3>
          <p class="text-2xl font-bold text-blue-600">{{ Math.max(Number((storyResult.data.evaluation_score.BLEU).toFixed(3)), 0.001)}}</p>
          <div class="w-full bg-gray-200 rounded-full h-4">
            <div
              class="bg-blue-600 h-4 rounded-full"
              :style="{ width: `${storyResult.data.evaluation_score.BLEU * 100}%` }"
            ></div>
          </div>
        </div>
        <div class="w-1/4 p-4 border border-gray-950/[.1] bg-gray-950/[.01] p-4 hover:bg-gray-950/[.05] dark:border-gray-50/[.1] dark:bg-gray-50/[.10] dark:hover:bg-gray-50/[.15] shadow-md rounded-lg text-center">
          <h3 class="text-xl font-semibold text-gray-700">Coherence</h3>
          <p class="text-2xl font-bold text-green-600">{{ storyResult.data.evaluation_score.Coherence.toFixed(3) }}</p>
          <div class="w-full bg-gray-200 rounded-full h-4">
            <div
              class="bg-green-600 h-4 rounded-full"
              :style="{ width: `${storyResult.data.evaluation_score.Coherence * 100}%` }"
            ></div>
          </div>
        </div>
        <div class="w-1/4 p-4  border border-gray-950/[.1] bg-gray-950/[.01] p-4 hover:bg-gray-950/[.05] dark:border-gray-50/[.1] dark:bg-gray-50/[.10] dark:hover:bg-gray-50/[.15] shadow-md rounded-lg text-center">
          <h3 class="text-xl font-semibold text-gray-700">Relevance</h3>
          <p class="text-2xl font-bold text-purple-600">{{ storyResult.data.evaluation_score.Relevance.toFixed(3) }}</p>
          <div class="w-full bg-gray-200 rounded-full h-4">
            <div
              class="bg-purple-600 h-4 rounded-full"
              :style="{ width: `${storyResult.data.evaluation_score.Relevance * 100}%` }"
            ></div>
          </div>
        </div>
        <div class="w-1/4 p-4  border border-gray-950/[.1] bg-gray-950/[.01] p-4 hover:bg-gray-950/[.05] dark:border-gray-50/[.1] dark:bg-gray-50/[.10] dark:hover:bg-gray-50/[.15] shadow-md rounded-lg text-center">
          <h3 class="text-xl font-semibold text-gray-700">Creativity</h3>
          <p class="text-2xl font-bold text-red-600">{{ storyResult.data.evaluation_score.Creativity.toFixed(3) }}</p>
          <div class="w-full bg-gray-200 rounded-full h-4">
            <div
              class="bg-red-600 h-4 rounded-full"
              :style="{ width: `${storyResult.data.evaluation_score.Creativity * 100}%` }"
            ></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import type { StoryResult } from "~/type/ChatMessage.type";
const storyResult = defineModel<StoryResult>();

const debounceTimeout = ref<NodeJS.Timeout | undefined>();

const onContentChange = (event: Event) => {
  const newContent = (event.target as HTMLElement).innerText;
  clearTimeout(debounceTimeout.value);
  debounceTimeout.value = setTimeout(() => {
    if (storyResult.value) {
      storyResult.value.data.content = newContent;
    }
  }, 1500);
};

</script>

<style></style>
