<template>
  <Splitter class="h-dvh">
    <SplitterPanel :minSize="20">
      <StoryBoard v-model="currentStoryBoard" />
    </SplitterPanel>
    <SplitterPanel :size="10" :minSize="20">
      <div class="flex flex-col h-full">
        <div class="scroller">
          <div class="scroller-content px-4">
            <ChatMessage
              v-for="message in messages"
              :key="message.id + message.type"
              :message="message"
              @switch-version="switchVersion"
            />
          </div>
        </div>
        <ChatInputUI v-model:input="input" @send-message="send" />
      </div>
    </SplitterPanel>
  </Splitter>
</template>

<script lang="ts" setup>
import type {
  ChatMessage,
  StoryResult,
  SearchResult,
  DataExtracted,
} from "~/type/ChatMessage.type";
const backend = useBackend();
const input = ref<string>("");
const messages = ref<ChatMessage[]>([]);
const currentStoryBoard = ref({
  id: "",
  dataExtracted: null as null | DataExtracted,
  searchResult: null as null | SearchResult,
  storyResult: null as null | StoryResult,
});

const send = async () => {
  const id = Math.random().toString(36).substring(7);
  messages.value.push({
    type: "user",
    content: input.value,
    id: id,
    steps: [],
  });
  messages.value.push({
    type: "bot",
    content: "",
    id: id,
    steps: [],
  });
  await backend.sendMessage({
    messages: messages.value,
    currentStoryBoard: currentStoryBoard.value,
  });
};

const switchVersion = (
  steps: (DataExtracted | SearchResult | StoryResult)[]
) => {
  for (const step of steps) {
    if (step.type === "extracted") {
      currentStoryBoard.value.dataExtracted = step;
    }
    if (step.type === "searchResult") {
      currentStoryBoard.value.searchResult = step;
    }
    if (step.type === "storyResult") {
      currentStoryBoard.value.storyResult = step;
    }
  }
};

backend.on.message((message) => {
  console.log("Updating message", message);
  const index = messages.value.findIndex(
    (m) => m.id === message.id && m.type === "bot"
  );
  if (index === -1) {
    return;
  }
  messages.value[index] = message;
  message.steps.find((step) => {
    if (step.type === "extracted") {
      currentStoryBoard.value.dataExtracted = step;
    }
    if (step.type === "searchResult") {
      currentStoryBoard.value.searchResult = step;
    }
    if (step.type === "storyResult") {
      currentStoryBoard.value.storyResult = step;
    }
  });
});

backend.on.storyBoardUpdate((storyBoard) => {
  currentStoryBoard.value.storyResult = {
    type: "storyResult",
    data: {
      title:
        storyBoard.title ||
        currentStoryBoard.value.storyResult?.data.title ||
        "",
      content:
        storyBoard.content ||
        currentStoryBoard.value.storyResult?.data.content ||
        "",
      image:
        storyBoard.image ||
        currentStoryBoard.value.storyResult?.data.image ||
        "",
    },
  };
});
</script>

<style>
.scroller {
  overflow: auto;
  height: 100%;
  display: flex;
  flex-direction: column-reverse;
  overflow-anchor: auto !important;
}

.scroller-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
</style>
