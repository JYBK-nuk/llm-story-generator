<template>
  <Splitter class="h-dvh">
    <SplitterPanel class="flex items-center justify-center" :minSize="20">
      Panel 1
    </SplitterPanel>
    <SplitterPanel :size="10" :minSize="20">
      <div class="flex flex-col h-full">
        <div class="scroller">
          <div class="scroller-content px-4">
            <ChatMessage
              v-for="message in messages"
              :key="message.id + message.type"
              :message="message"
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
  steps: [] as (DataExtracted | SearchResult | StoryResult)[],
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
    content: "dd",
    id: id,
    steps: [],
  });
  await backend.sendMessage({
    messages: messages.value,
    currentSteps: currentStoryBoard.value.steps,
  });
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
  currentStoryBoard.value.steps = message.steps;
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
