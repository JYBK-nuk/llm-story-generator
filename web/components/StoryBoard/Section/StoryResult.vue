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
