<template>
  <div
    v-if="currentStoryBoard"
    class="p-4 flex-col flex gap-5 overflow-y-auto h-full"
  >
    <div
      class="opacity-70 text-sm font-bold"
      v-if="currentStoryBoard.dataExtracted"
    >
      故事板
    </div>
    <div class="px-2">
      <StoryBoardSectionExtracted
        v-if="currentStoryBoard.dataExtracted"
        v-model="currentStoryBoard.dataExtracted"
      />
    </div>
    <div
      class="opacity-70 text-sm font-bold"
      v-if="currentStoryBoard.searchResult"
    >
      搜尋結果
    </div>
    <div class="px-2">
      <StoryBoardSectionSearchResult
        v-if="currentStoryBoard.searchResult"
        v-model="currentStoryBoard.searchResult"
      />
    </div>

    <div
      class="opacity-70 text-sm font-bold"
      v-if="currentStoryBoard.storyResult"
    >
      故事結果
    </div>
    <div class="px-2" v-auto-animate v-if="currentStoryBoard.storyResult">
      <StoryBoardSectionStoryResult v-model="currentStoryBoard.storyResult" />
    </div>
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

<style scoped></style>
