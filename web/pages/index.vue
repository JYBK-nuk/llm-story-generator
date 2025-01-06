<template>
  <Splitter class="h-dvh">
    <SplitterPanel class="flex items-center justify-center" :minSize="20">
      Panel 1
    </SplitterPanel>
    <SplitterPanel :size="10" :minSize="20">
      <div class="flex flex-col h-full">
        <div class="scroller">
          <div class="scroller-content px-5">
            <ChatMessage
              v-for="message in messages"
              :key="message.id"
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
import type { ChatMessage } from "~/type/ChatMessage.type";
const backend = useBackend();
const input = ref<string>("");
const messages = ref<ChatMessage[]>([
  {
    type: "user",
    content: "Hello, I'm a bot!",
    id: "3",
    steps: [],
  },
  {
    type: "bot",
    content: "Hello, I'm a bot!",
    id: "1",
    steps: [],
  },
]);

const send = async () => {
  messages.value.push({
    type: "user",
    content: input.value,
    id: Math.random().toString(36).substring(7),
    steps: [],
  });
  await backend.sendMessage(messages.value);
};
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
