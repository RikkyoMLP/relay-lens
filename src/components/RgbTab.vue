<script setup lang="ts">
import { computed } from "vue";
import { useFileStore } from "@/stores/fileStore";
import { vizUrl, getSceneCount } from "@/api/client";
import SceneGrid from "./SceneGrid.vue";

const fileStore = useFileStore();

const sections = computed(() => {
  const key = fileStore.selectedKey;
  if (!key) return [];

  return fileStore.filesArray
    .map((file) => {
      const keyInfo = file.keys.find((k) => k.name === key);
      if (!keyInfo) return null;
      const count = getSceneCount(keyInfo);
      if (count === 0) return null;

      // RGB images for all scenes
      const rgbUrls = Array.from({ length: count }, (_, i) =>
        vizUrl("rgb", { file_id: file.fileId, key, scene: i }),
      );

      // Check if there's a plausible truth key for error maps
      const truthKey = key !== "truth" ? file.keys.find((k) => k.name === "truth") : null;
      let errorUrls: string[] = [];
      if (truthKey && getSceneCount(truthKey) === count) {
        errorUrls = Array.from({ length: count }, (_, i) =>
          vizUrl("error-map", {
            file_id: file.fileId,
            pred_key: key,
            truth_key: "truth",
            scene: i,
          }),
        );
      }

      return { file, rgbUrls, errorUrls };
    })
    .filter(Boolean);
});
</script>

<template>
  <div v-if="!fileStore.selectedKey" class="empty-state">
    <el-empty description="Select a key from the toolbar to visualize" :image-size="64" />
  </div>

  <div v-else-if="sections.length === 0" class="empty-state">
    <el-empty description="No HSI data for the selected key" :image-size="64" />
  </div>

  <div v-else>
    <div v-for="section in sections" :key="section!.file.fileId" class="file-block">
      <SceneGrid :image-urls="section!.rgbUrls" :label="`${section!.file.filename} - RGB`" />

      <SceneGrid
        v-if="section!.errorUrls.length > 0"
        :image-urls="section!.errorUrls"
        :label="`${section!.file.filename} - Error Map (vs truth)`"
      />
    </div>
  </div>
</template>

<style lang="scss" scoped>
.empty-state {
  padding: 48px 0;
}

.file-block {
  margin-bottom: 24px;
}
</style>
