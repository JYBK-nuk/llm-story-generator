<template>
  <div>
    {{ currentStoryBoard }}
  </div>
</template>

<script lang="ts" setup>
import type {
  ChatMessage,
  StoryResult,
  SearchResult,
  DataExtracted,
} from "~/type/ChatMessage.type";

const currentStoryBoard = defineModel<{
  id: string;
  dataExtracted: null | DataExtracted;
  searchResult: null | SearchResult;
  storyResult: null | StoryResult;
}>();
</script>

<style></style>
