<template>
  <div>
    <img
      :src="props.url"
      :alt="props.prompt"
      class="w-270px"
      :title="props.prompt"
    />
  </div>
</template>

<script lang="ts" setup>
const props = defineProps<{
  url: string;
  prompt: string;
}>();
</script>

<style></style>
