<template>
  <Splitter class="h-dvh">
    <SplitterPanel :minSize="20">
      <StoryBoard v-model="currentStoryBoard" />
    </SplitterPanel>
    <SplitterPanel :size="10" :minSize="20">
      <div class="flex flex-col h-full">
        <div class="p-2 flex flex-col gap-1 w-full">
          <Select
            v-model="selectedSessionId"
            :options="sessions"
            option-value="sid"
            option-label="title"
            class="w-full"
            @value-change="changeSession"
          />
          <Button
            label="+ 新聊天"
            fluid
            severity="secondary"
            text
            size="small"
            @click="changeSession(null)"
          />
        </div>
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
import { useUrlSearchParams } from "@vueuse/core";
import type {
  ChatMessage,
  StoryResult,
  SearchResult,
  DataExtracted,
} from "~/type/ChatMessage.type";
const sessionsStore = useSessionsStore();
const params = useUrlSearchParams("history");
const backend = useBackend();
const input = ref<string>("");

const sessions = computed(() => sessionsStore.sessions);
const selectedSessionId = ref<string | null>(null);

const messages = ref<ChatMessage[]>([]);
const currentStoryBoard = ref({
  id: "",
  dataExtracted: null as null | DataExtracted,
  searchResult: null as null | SearchResult,
  storyResult: null as null | StoryResult,
});

onMounted(() => {
  selectedSessionId.value = params.sid as string;
  changeSession(selectedSessionId.value);
});

const changeSession = async (session_id: string | null | { sid: string }) => {
  if (typeof session_id != "string" && session_id) {
    session_id = session_id.sid;
  }

  sessionsStore.init();
  if (session_id) {
    selectedSessionId.value = session_id;
    params.sid = session_id;
    const session = sessionsStore.getSession(session_id);
    if (session) {
      messages.value = session.messages;
      return;
    }
  }
  const sid = sessionsStore.addSession();
  params.sid = sid;
  selectedSessionId.value = sid;
  messages.value = [];
};

const resetStoryBoard = () => {
  currentStoryBoard.value = {
    id: "",
    dataExtracted: null,
    searchResult: null,
    storyResult: null,
  };
};

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
  if (selectedSessionId.value) {
    sessionsStore.updateSession(selectedSessionId.value, messages.value);
  }
  input.value = "";
};

const switchVersion = (
  steps: (DataExtracted | SearchResult | StoryResult)[]
) => {
  resetStoryBoard();
  nextTick(() => {
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
  });
};

backend.on.message((message) => {
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
  if (selectedSessionId.value) {
    sessionsStore.updateSession(selectedSessionId.value, messages.value);
  }
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
      image_prompt:
        storyBoard.image_prompt ||
        currentStoryBoard.value.storyResult?.data.image_prompt ||
        "",
      evaluation_score:
        storyBoard.evaluation_score ||
        currentStoryBoard.value.storyResult?.data.evaluation_score ||
        null,
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

.p-select-list-container {
  max-width: 500px;
}
</style>
