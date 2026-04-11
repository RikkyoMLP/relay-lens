<script setup lang="ts">
import { computed, ref } from "vue";
import { useFileStore } from "@/stores/fileStore";
import { useVizStore } from "@/stores/vizStore";
import { vizUrl, getSceneCount } from "@/api/client";
import SceneGrid from "./SceneGrid.vue";
import type { UploadFile } from "element-plus";

const fileStore = useFileStore();
const vizStore = useVizStore();
const scanning = ref(false);
const uploading = ref(false);

const sections = computed(() => {
  const key = fileStore.selectedKey;
  if (!key || !vizStore.maskStatus.loaded) return [];

  return fileStore.filesArray
    .map((file) => {
      const keyInfo = file.keys.find((k) => k.name === key);
      if (!keyInfo) return null;
      const count = getSceneCount(keyInfo);
      if (count === 0) return null;

      const urls = Array.from({ length: count }, (_, i) =>
        vizUrl("measurement", { file_id: file.fileId, key, scene: i }),
      );
      return { file, urls };
    })
    .filter(Boolean);
});

async function handleScanMask() {
  scanning.value = true;
  try {
    await vizStore.scanMask();
  } catch {
    // scan-mask 404 means no mask found, not a crash
  } finally {
    scanning.value = false;
  }
}

async function handleUploadMask(uploadFile: UploadFile) {
  if (!uploadFile.raw) return;
  uploading.value = true;
  try {
    await vizStore.uploadMask(uploadFile.raw);
  } finally {
    uploading.value = false;
  }
}
</script>

<template>
  <div>
    <!-- Mask controls -->
    <div class="mask-controls">
      <div class="mask-controls__status">
        <el-tag v-if="vizStore.maskStatus.loaded" type="success" effect="plain">
          Mask: {{ vizStore.maskStatus.filename }} ({{ vizStore.maskStatus.shape?.join(" x ") }})
        </el-tag>
        <el-tag v-else type="info" effect="plain">No mask loaded</el-tag>
      </div>
      <div class="mask-controls__actions">
        <el-button size="small" :loading="scanning" @click="handleScanMask"> Scan Mask </el-button>
        <el-upload
          accept=".mat"
          :auto-upload="false"
          :show-file-list="false"
          :on-change="handleUploadMask"
        >
          <el-button size="small" :loading="uploading">Upload Mask</el-button>
        </el-upload>
      </div>
    </div>

    <!-- Empty states -->
    <div v-if="!vizStore.maskStatus.loaded" class="py-12">
      <el-empty description="Load a mask file to compute CASSI measurements" :image-size="64" />
    </div>

    <div v-else-if="!fileStore.selectedKey" class="py-12">
      <el-empty description="Select a key from the toolbar" :image-size="64" />
    </div>

    <div v-else-if="sections.length === 0" class="py-12">
      <el-empty description="No HSI data for the selected key" :image-size="64" />
    </div>

    <!-- Measurement images -->
    <div v-else>
      <div v-for="section in sections" :key="section!.file.fileId" class="mb-6">
        <SceneGrid :image-urls="section!.urls" :label="`${section!.file.filename} - Measurement`" />
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.mask-controls {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
  padding: 8px 0;
  border-bottom: 1px solid var(--el-border-color-lighter);

  &__actions {
    display: flex;
    gap: 8px;
    align-items: center;
  }
}
</style>
