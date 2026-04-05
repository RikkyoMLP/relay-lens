<script setup lang="ts">
import { onMounted } from "vue";
import { useFileStore } from "@/stores/fileStore";
import SidebarPanel from "./components/SidebarPanel.vue";
import MainPanel from "./components/MainPanel.vue";

const fileStore = useFileStore();

onMounted(() => {
  fileStore.scanLocal();
});
</script>

<template>
  <el-container class="app-layout">
    <el-aside width="300px" class="app-sidebar">
      <SidebarPanel />
    </el-aside>
    <el-main class="app-main">
      <MainPanel />
    </el-main>
  </el-container>
</template>

<style lang="scss" scoped>
.app-layout {
  height: 100vh;
}

.app-sidebar {
  border-right: 1px solid var(--el-border-color);
  overflow-y: auto;
  padding: 16px;
  background: var(--el-bg-color-page);
}

.app-main {
  overflow-y: auto;
  padding: 16px;
}
</style>
