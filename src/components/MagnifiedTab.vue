<script setup lang="ts">
import { computed } from "vue";
import { useFileStore } from "@/stores/fileStore";
import { useVizStore } from "@/stores/vizStore";
import { vizUrl, getSceneCount } from "@/api/client";
import SceneGrid from "./SceneGrid.vue";

const fileStore = useFileStore();
const vizStore = useVizStore();

const sections = computed(() => {
  const key = fileStore.selectedKey;
  if (!key) return [];

  return fileStore.filesArray
    .map((file) => {
      const keyInfo = file.keys.find((k) => k.name === key);
      if (!keyInfo) return null;
      const count = getSceneCount(keyInfo);
      if (count === 0) return null;

      // Build magnified URLs for each selected channel
      const channels = vizStore.selectedChannels.map((ch) => {
        const urls = Array.from({ length: count }, (_, i) =>
          vizUrl("magnified", {
            file_id: file.fileId,
            key,
            scene: i,
            channel: ch,
            roi_x: vizStore.roi.x,
            roi_y: vizStore.roi.y,
            roi_w: vizStore.roi.w,
            roi_h: vizStore.roi.h,
          }),
        );
        return { ch, urls };
      });

      return { file, channels };
    })
    .filter(Boolean);
});
</script>

<template>
  <div v-if="!fileStore.selectedKey">
    <el-empty description="Select a key to visualize" :image-size="64" />
  </div>

  <div v-else-if="sections.length === 0">
    <el-empty description="No HSI data for the selected key" :image-size="64" />
  </div>

  <div v-else>
    <div v-for="section in sections" :key="section!.file.fileId" class="file-block">
      <template v-for="chData in section!.channels" :key="chData.ch">
        <SceneGrid
          :image-urls="chData.urls"
          :label="`${section!.file.filename} - ch${chData.ch} (magnified)`"
        />
      </template>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.file-block {
  margin-bottom: 24px;
}
</style>
