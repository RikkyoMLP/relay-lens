<script setup lang="ts">
import { computed } from "vue";
import { useFileStore } from "@/stores/fileStore";
import { useVizStore } from "@/stores/vizStore";
import { dataTypeLabel, formatShape } from "@/api/client";

const fileStore = useFileStore();
const vizStore = useVizStore();

// Mirror of hsi_utils WAVELENGTHS_28 / WAVELENGTHS_31
const WAVELENGTHS: Record<number, number[]> = {
  28: [
    453.5, 457.5, 462, 466, 471.5, 476.5, 481.5, 487, 492.5, 498, 504, 510,
    516, 522.5, 529.5, 536.5, 544, 551.5, 558.5, 567.5, 575.5, 584.5, 594.5,
    604, 614.5, 625, 636.5, 648,
  ],
  31: Array.from({ length: 31 }, (_, i) => 400 + i * 10),
};

const channelCount = computed(() => {
  const key = fileStore.commonKeys.find((k) => k.name === fileStore.selectedKey);
  if (!key) return 28;
  return key.shape[key.shape.length - 1];
});

const channelLabels = computed(() => {
  const n = channelCount.value;
  const wl = WAVELENGTHS[n];
  return Array.from({ length: n }, (_, i) =>
    wl ? `ch${i + 1} (${wl[i]}nm)` : `ch${i}`,
  );
});
</script>

<template>
  <div class="viz-toolbar">
    <div class="viz-toolbar__row">
      <!-- Key selector -->
      <div class="viz-toolbar__item">
        <label class="viz-toolbar__label">Key</label>
        <el-select
          v-model="fileStore.selectedKey"
          placeholder="Select key"
          style="width: 200px"
          :disabled="fileStore.commonKeys.length === 0"
        >
          <el-option
            v-for="key in fileStore.commonKeys"
            :key="key.name"
            :label="key.name"
            :value="key.name"
          >
            <span>{{ key.name }}</span>
            <el-tag size="small" effect="plain" style="margin-left: 8px">
              {{ dataTypeLabel(key.dataType) }}
            </el-tag>
            <span style="margin-left: 4px; font-size: 11px; color: #999; font-family: monospace">
              {{ formatShape(key.shape) }}
            </span>
          </el-option>
        </el-select>
      </div>

      <!-- Channel selector -->
      <div class="viz-toolbar__item">
        <label class="viz-toolbar__label">Channels</label>
        <el-select
          v-model="vizStore.selectedChannels"
          multiple
          collapse-tags
          collapse-tags-tooltip
          placeholder="Channels"
          style="width: 220px"
        >
          <el-option v-for="(label, i) in channelLabels" :key="i" :label="label" :value="i" />
        </el-select>
      </div>

      <!-- ROI inputs -->
      <div class="viz-toolbar__item">
        <label class="viz-toolbar__label">ROI</label>
        <div class="viz-toolbar__roi">
          <el-input-number
            v-model="vizStore.roi.x"
            :min="0"
            :step="10"
            size="small"
            controls-position="right"
          />
          <el-input-number
            v-model="vizStore.roi.y"
            :min="0"
            :step="10"
            size="small"
            controls-position="right"
          />
          <el-input-number
            v-model="vizStore.roi.w"
            :min="1"
            :step="10"
            size="small"
            controls-position="right"
          />
          <el-input-number
            v-model="vizStore.roi.h"
            :min="1"
            :step="10"
            size="small"
            controls-position="right"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.viz-toolbar {
  padding: 8px 0 12px;
  border-bottom: 1px solid var(--el-border-color-lighter);
  margin-bottom: 12px;

  &__row {
    display: flex;
    flex-wrap: wrap;
    gap: 16px;
    align-items: flex-end;
  }

  &__item {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  &__label {
    font-size: 12px;
    font-weight: 600;
    color: var(--el-text-color-secondary);
  }

  &__roi {
    display: flex;
    gap: 4px;

    .el-input-number {
      width: 80px;
    }
  }
}
</style>
