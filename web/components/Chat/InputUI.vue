<template>
  <div class="p-3 w-full flex gap-2 mt-auto">
    <div class="w-full">
      <IInput v-model="input" placeholder="輸入你想要的故事" />
    </div>
    <div class="flex">
      <IButton @click="sendMessage">
        <Icon name="mingcute:send-fill" />
      </IButton>
    </div>
  </div>
</template>

<script lang="ts" setup>
const input = defineModel<string>("input", { default: "" });
const sendMessage = () => {
  emits("sendMessage", input.value);
};

const emits = defineEmits<{
  (e: "sendMessage", payload: string): void;
}>();
</script>

<style></style>
