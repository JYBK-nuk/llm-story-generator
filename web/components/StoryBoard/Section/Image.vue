<template>
  <div class="flex justify-center">
    {{ props.url }}
    <img :src="props.url" class="max-w-full" />
  </div>
</template>

<script lang="ts" setup>
const props = defineProps<{
  url: string;
}>();
</script>

<style></style>
