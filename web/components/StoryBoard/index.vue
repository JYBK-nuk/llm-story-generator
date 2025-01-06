<template>
  <div v-if="currentStoryBoard" class="p-4 flex-col flex gap-3">
    <StoryBoardSectionExtracted
      v-if="currentStoryBoard.dataExtracted"
      v-model="currentStoryBoard.dataExtracted"
    />

    <StoryBoardSectionSearchResult
      v-if="currentStoryBoard.searchResult"
      v-model="currentStoryBoard.searchResult"
    />

    <StoryBoardSectionStoryResult
      v-if="currentStoryBoard.storyResult"
      v-model="currentStoryBoard.storyResult"
    />
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
