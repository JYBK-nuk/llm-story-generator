<template>
  <div
    v-if="currentStoryBoard"
    class="overflow-y-auto h-full relative overflow-x-hidden"
  >
    <ClientOnly>
      <IBlurReveal :delay="0.1" :duration="0.75">
        <div class="flex-col flex gap-5 pb-50px pt-2 px-4" v-auto-animate>
          <div v-if="currentStoryBoard.dataExtracted">
            <div class="opacity-70 text-sm font-bold">故事板</div>
            <div class="px-2">
              <StoryBoardSectionExtracted
                v-model="currentStoryBoard.dataExtracted"
              />
            </div>
          </div>
          <div v-if="currentStoryBoard.searchResult?.data.length">
            <div class="opacity-70 text-sm font-bold">搜尋結果</div>
            <div class="px-2">
              <StoryBoardSectionSearchResult
                v-model="currentStoryBoard.searchResult"
              />
            </div>
          </div>

          <div v-if="currentStoryBoard.storyResult">
            <div class="opacity-70 text-sm font-bold">故事結果</div>
            <div class="px-2">
              <StoryBoardSectionStoryResult
                v-model="currentStoryBoard.storyResult"
              />
            </div>
          </div></div
      ></IBlurReveal>
    </ClientOnly>
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
