<template>
  <div>
    <img :src="props.url" class="w-270px" />
  </div>
</template>

<script lang="ts" setup>
const props = defineProps<{
  url: string;
}>();
</script>

<style></style>
