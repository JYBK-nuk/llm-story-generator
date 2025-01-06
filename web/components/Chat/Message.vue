<template>
  <div>
    <div class="flex justify-end" v-if="message.type == 'user'">
      <div class="bg-blue-500 text-white p-2 rounded-lg">
        {{ message.content }}
      </div>
    </div>

    <div class="flex flex-col gap-2" v-else>
      <div>{{ message.content }}</div>
      <div class="flex items-center gap-2 bg-slate-100 p-2 rounded-lg">
        <Icon name="line-md:loading-twotone-loop" />
        <p>{{ statusText }}</p>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import type { ChatMessage } from "~/type/ChatMessage.type";

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
      return "完成！";
  }
});
</script>

<style></style>
