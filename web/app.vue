<template>
  <div>
    <input type="text" v-model="data.name.value" />
    <button @click="send">send</button>
  </div>
</template>
<script lang="ts" setup>
const backend = useBackend();
const data = {
  name: ref(""),
};

const send = () => {
  backend.sendName(data.name.value);
};
</script>
