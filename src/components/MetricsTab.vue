<script setup lang="ts">
import { computed } from "vue";
import { useFileStore } from "@/stores/fileStore";
import { vizUrl } from "@/api/client";

const fileStore = useFileStore();

const sections = computed(() => {
  return fileStore.filesArray
    .map((file) => {
      // Find all metric_array keys
      const metricKeys = file.keys.filter((k) => k.dataType === "metric_array").map((k) => k.name);

      if (metricKeys.length === 0) return null;

      const imgUrl = vizUrl("metrics", {
        file_id: file.fileId,
        keys: metricKeys.join(","),
      });

      return { file, imgUrl, metricKeys };
    })
    .filter(Boolean);
});
</script>

<template>
  <div v-if="sections.length === 0">
    <el-empty description="No metric arrays found in loaded files" :image-size="64" />
  </div>

  <div v-else>
    <div v-for="section in sections" :key="section!.file.fileId" class="metrics-block">
      <div class="file-section-header">
        {{ section!.file.filename }} ({{ section!.metricKeys.join(", ") }})
      </div>
      <img :src="section!.imgUrl" class="metrics-block__plot" loading="lazy" />
    </div>
  </div>
</template>

<style lang="scss" scoped>
.metrics-block {
  margin-bottom: 24px;

  &__plot {
    max-width: 100%;
    border: 1px solid var(--el-border-color-lighter);
    border-radius: 4px;
  }
}
</style>
