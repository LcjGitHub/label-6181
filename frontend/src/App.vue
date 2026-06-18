<script setup lang="ts">
import { NConfigProvider, NMessageProvider, zhCN, dateZhCN } from 'naive-ui'
import { RouterView } from 'vue-router'
</script>

<template>
  <NConfigProvider :locale="zhCN" :date-locale="dateZhCN">
    <NMessageProvider>
      <RouterView />
    </NMessageProvider>
  </NConfigProvider>
</template>

<style>
* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background: #f5f0e8;
  color: #2c2416;
}

#app {
  min-height: 100vh;
}
</style>
