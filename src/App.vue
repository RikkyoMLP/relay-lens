<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useFileStore } from "@/stores/fileStore";
import SidebarPanel from "./components/SidebarPanel.vue";
import MainPanel from "./components/MainPanel.vue";

const fileStore = useFileStore();
const sidebarWidth = ref(300);
const dragging = ref(false);

onMounted(() => {
  fileStore.scanLocal();
});

function onDragStart(e: MouseEvent) {
  e.preventDefault();
  dragging.value = true;
  const onMove = (ev: MouseEvent) => {
    sidebarWidth.value = Math.min(600, Math.max(200, ev.clientX));
  };
  const onUp = () => {
    dragging.value = false;
    document.removeEventListener("mousemove", onMove);
    document.removeEventListener("mouseup", onUp);
  };
  document.addEventListener("mousemove", onMove);
  document.addEventListener("mouseup", onUp);
}
</script>

<template>
  <el-container
    class="app-layout"
    :class="{ 'app-layout--dragging': dragging }"
  >
    <el-aside
      :width="`${sidebarWidth}px`"
      class="app-layout__sidebar border-r-none overflow-y-auto p-4 bg-[var(--el-bg-color-page)]"
    >
      <SidebarPanel />
    </el-aside>
    <div class="app-layout__resizer" @mousedown="onDragStart" />
    <el-main class="app-layout__main">
      <MainPanel />
    </el-main>
  </el-container>
</template>

<style lang="scss" scoped>
.app-layout {
  height: 100vh;

  &--dragging {
    user-select: none;
    cursor: col-resize;
  }

  &__resizer {
    width: 4px;
    flex-shrink: 0;
    cursor: col-resize;
    position: relative;

    &::before,
    &::after {
      content: "";
      position: absolute;
      top: 0;
      bottom: 0;
      width: 2px;
    }

    &::before {
      left: 0;
      background: var(--el-bg-color-page);
    }

    &::after {
      left: 50%;
      transform: translateX(-50%);
      background: var(--el-border-color);
      transition: background 0.15s;
    }

    &:hover::after {
      background: var(--el-color-primary);
    }
  }

  &__main {
    overflow-y: auto;
    padding: 16px;
  }
}
</style>
