import { defineStore } from "pinia";
import { ref, computed } from "vue";
import {
  scanLocalFiles,
  uploadFiles as apiUploadFiles,
  getCommonKeys,
  deleteFile as apiDeleteFile,
  type FileEntry,
  type KeyInfo,
} from "@/api/client";

export const useFileStore = defineStore("files", () => {
  const files = ref<Record<string, FileEntry>>({});
  const commonKeys = ref<KeyInfo[]>([]);
  const selectedKey = ref<string | null>(null);

  const filesArray = computed(() => Object.values(files.value));

  async function scanLocal() {
    const result = await scanLocalFiles();
    for (const f of result) {
      files.value[f.fileId] = f;
    }
    await refreshCommonKeys();
  }

  async function uploadFiles(rawFiles: File[]) {
    const result = await apiUploadFiles(rawFiles);
    for (const f of result) {
      files.value[f.fileId] = f;
    }
    await refreshCommonKeys();
  }

  async function refreshCommonKeys() {
    commonKeys.value = await getCommonKeys();
    // Auto-select first HSI key if none selected
    if (!selectedKey.value && commonKeys.value.length > 0) {
      const hsiKey = commonKeys.value.find(
        (k) => k.dataType === "hsi_cube_batch" || k.dataType === "hsi_cube",
      );
      selectedKey.value = hsiKey?.name ?? commonKeys.value[0].name;
    }
  }

  async function removeFile(fileId: string) {
    await apiDeleteFile(fileId);
    delete files.value[fileId];
    await refreshCommonKeys();
  }

  return {
    files,
    filesArray,
    commonKeys,
    selectedKey,
    scanLocal,
    uploadFiles,
    removeFile,
    refreshCommonKeys,
  };
});
