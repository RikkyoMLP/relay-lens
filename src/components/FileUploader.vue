<script setup lang="ts">
import { ref } from "vue";
import { useFileStore } from "@/stores/fileStore";
import type { UploadFile, UploadInstance } from "element-plus";

const fileStore = useFileStore();
const uploadRef = ref<UploadInstance>();
const uploading = ref(false);

async function handleChange(uploadFile: UploadFile) {
  if (!uploadFile.raw) return;
  uploading.value = true;
  try {
    await fileStore.uploadFiles([uploadFile.raw]);
  } finally {
    uploading.value = false;
    uploadRef.value?.clearFiles();
  }
}

async function scanLocal() {
  await fileStore.scanLocal();
}
</script>

<template>
  <div class="file-uploader">
    <el-upload
      ref="uploadRef"
      drag
      multiple
      accept=".mat"
      :auto-upload="false"
      :on-change="handleChange"
      :show-file-list="false"
    >
      <div class="file-uploader__hint">
        <p v-if="uploading">Uploading...</p>
        <template v-else>
          <p>Drop .mat files here</p>
          <p class="file-uploader__hint--sub">or click to browse</p>
        </template>
      </div>
    </el-upload>

    <div class="file-uploader__actions">
      <el-button size="small" @click="scanLocal"> Scan Local </el-button>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.file-uploader {
  &__hint {
    padding: 8px 0;

    p {
      margin: 0;
      font-size: 13px;
      color: var(--el-text-color-regular);
    }

    &--sub {
      font-size: 12px;
      color: var(--el-text-color-placeholder);
    }
  }

  &__actions {
    display: flex;
    gap: 8px;
    margin-top: 8px;
  }
}
</style>
