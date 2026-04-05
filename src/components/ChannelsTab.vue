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

      const truthKey = key !== "truth" ? file.keys.find((k) => k.name === "truth") : null;
      const hasTruth = truthKey && getSceneCount(truthKey) === count;

      // For each selected channel, build colorized + diff URLs
      const channels = vizStore.selectedChannels.map((ch) => {
        const colorUrls = Array.from({ length: count }, (_, i) =>
          vizUrl("colorized", { file_id: file.fileId, key, scene: i, channel: ch }),
        );
        let diffUrls: string[] = [];
        if (hasTruth) {
          diffUrls = Array.from({ length: count }, (_, i) =>
            vizUrl("error-map", {
              file_id: file.fileId,
              pred_key: key,
              truth_key: "truth",
              scene: i,
              channel: ch,
            }),
          );
        }
        return { ch, colorUrls, diffUrls };
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
          :image-urls="chData.colorUrls"
          :label="`${section!.file.filename} - ch${chData.ch}`"
        />
        <SceneGrid
          v-if="chData.diffUrls.length > 0"
          :image-urls="chData.diffUrls"
          :label="`${section!.file.filename} - ch${chData.ch} diff`"
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
