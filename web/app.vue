
<template>
  <div>
    <input type="text" v-model="data.name" />
    <button @click="methods.send">send</button>
  </div>
</template>
<script lang="ts">

const backend = useBackend();
const data = {
  name: ref(''),
}

const send = () => {
};
