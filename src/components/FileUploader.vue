<script setup lang="ts">
import { ref } from "vue";
import { useFileStore } from "@/stores/fileStore";
import type { UploadFile } from "element-plus";

const fileStore = useFileStore();
const pendingFiles = ref<File[]>([]);
const uploading = ref(false);

function handleChange(uploadFile: UploadFile) {
  if (uploadFile.raw) {
    pendingFiles.value.push(uploadFile.raw);
  }
}

function handleRemove(uploadFile: UploadFile) {
  const idx = pendingFiles.value.findIndex((f) => f.name === uploadFile.name);
  if (idx >= 0) pendingFiles.value.splice(idx, 1);
}

async function submitUpload() {
  if (pendingFiles.value.length === 0) return;
  uploading.value = true;
  try {
    await fileStore.uploadFiles(pendingFiles.value);
    pendingFiles.value = [];
  } finally {
    uploading.value = false;
  }
}

async function scanLocal() {
  await fileStore.scanLocal();
}
</script>

<template>
  <div class="file-uploader">
    <el-upload
      drag
      multiple
      accept=".mat"
      :auto-upload="false"
      :on-change="handleChange"
      :on-remove="handleRemove"
      :show-file-list="true"
    >
      <div class="file-uploader__hint">
        <p>Drop .mat files here</p>
        <p class="file-uploader__hint--sub">or click to browse</p>
      </div>
    </el-upload>

    <div class="file-uploader__actions">
      <el-button
        type="primary"
        size="small"
        :loading="uploading"
        :disabled="pendingFiles.length === 0"
        @click="submitUpload"
      >
        Upload ({{ pendingFiles.length }})
      </el-button>
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
