<template>
  <div v-if="storyResult" class="flex flex-col gap-3">
    <div class="font-bold text-lg">{{ storyResult.data.title }}</div>
    <div>{{ storyResult.data.content }}</div>
  </div>
</template>

<script lang="ts" setup>
import type { StoryResult } from "~/type/ChatMessage.type";
const storyResult = defineModel<StoryResult>();
</script>

<style></style>
