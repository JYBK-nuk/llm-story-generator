<template>
  <div>
    <div class="flex justify-end" v-if="message.type == 'user'">
      <div class="bg-blue-500 text-white p-2 rounded-lg">
        {{ message.content }}
      </div>
    </div>

    <div class="flex flex-col gap-2" v-else>
      <div>{{ message.content }}</div>
      <div class="flex items-center gap-2 bg-slate-100 rounded-lg px-3 py-2">
        <Icon
          :name="
            statusText == '完成'
              ? 'line-md:circle-twotone-to-confirm-circle-transition'
              : 'line-md:loading-twotone-loop'
          "
        />
        <p>{{ statusText === "完成" ? storyTitle : statusText }}</p>
        <div class="ml-auto" v-if="statusText == '完成'">切換到此版本</div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import type { ChatMessage, StoryResult } from "~/type/ChatMessage.type";

const props = defineProps<{
  message: ChatMessage;
}>();

const statusText = computed(() => {
  if (props.message.steps.length == 0) {
    return "提取元素中...";
  }
  const lastStep = props.message.steps[props.message.steps.length - 1].type;
  switch (lastStep) {
    case "extracted":
      return "搜尋新聞中...";
    case "searchResult":
      return "生成故事中...";
    case "storyResult":
      return "完成";
  }
});

const storyTitle = computed(() => {
  if (props.message.steps.length == 0) {
    return "";
  }
  const lastStep = props.message.steps[props.message.steps.length - 1];
  if (lastStep.type === "storyResult") {
    return lastStep.data.title;
  }
  return "";
});
</script>

<style></style>
