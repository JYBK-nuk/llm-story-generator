<template>
  <div v-if="storyResult" class="flex flex-col gap-3">
    <div class="font-bold text-lg">{{ storyResult.data.title }}</div>
    <div
      contenteditable="true"
      style="white-space: pre-wrap"
      @input="onContentChange"
    >
      {{ storyResult.data.content }}
    </div>
  </div>
</template>

<script lang="ts" setup>
import type { StoryResult } from "~/type/ChatMessage.type";
const storyResult = defineModel<StoryResult>();

const onContentChange = (event: Event) => {
  const newContent = (event.target as HTMLElement).innerText;
  if (storyResult.value) storyResult.value.data.content = newContent;
};
</script>

<style></style>
