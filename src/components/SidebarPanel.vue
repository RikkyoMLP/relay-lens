<script setup lang="ts">
import FileUploader from "./FileUploader.vue";
import FileTree from "./FileTree.vue";
</script>

<template>
  <div class="sidebar-panel">
    <h3 class="sidebar-title">Relay Lens</h3>
    <FileUploader />
    <el-divider />
    <FileTree />
  </div>
</template>

<style lang="scss" scoped>
.sidebar-title {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 16px;
  color: var(--el-text-color-primary);
}
</style>
