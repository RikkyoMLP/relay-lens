import { defineStore } from "pinia";
import { ref } from "vue";
import {
  scanMask as apiScanMask,
  uploadMask as apiUploadMask,
  getMaskStatus,
  type MaskStatus,
} from "@/api/client";

export const useVizStore = defineStore("viz", () => {
  const roi = ref({ x: 100, y: 80, w: 40, h: 40 });
  const selectedChannels = ref([2, 17, 26]);
  const activeTab = ref("rgb");
  const errorMapScale = ref(5.0);

  // Mask state
  const maskStatus = ref<MaskStatus>({ loaded: false });

  async function refreshMaskStatus() {
    maskStatus.value = await getMaskStatus();
  }

  async function scanMask() {
    maskStatus.value = await apiScanMask();
  }

  async function uploadMask(file: File) {
    maskStatus.value = await apiUploadMask(file);
  }

  return {
    roi,
    selectedChannels,
    activeTab,
    errorMapScale,
    maskStatus,
    refreshMaskStatus,
    scanMask,
    uploadMask,
  };
});
