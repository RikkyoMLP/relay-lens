<script setup lang="ts">
import { useVizStore } from "@/stores/vizStore";
import VizToolbar from "./VizToolbar.vue";
import RgbTab from "./RgbTab.vue";
import ChannelsTab from "./ChannelsTab.vue";
import MagnifiedTab from "./MagnifiedTab.vue";
import MetricsTab from "./MetricsTab.vue";
import SpectralDensityTab from "./SpectralDensityTab.vue";
import MeasurementTab from "./MeasurementTab.vue";

const vizStore = useVizStore();
</script>

<template>
  <div class="main-panel">
    <VizToolbar />

    <el-tabs v-model="vizStore.activeTab" class="main-panel__tabs">
      <el-tab-pane label="RGB" name="rgb">
        <RgbTab />
      </el-tab-pane>
      <el-tab-pane label="Channels" name="channels">
        <ChannelsTab />
      </el-tab-pane>
      <el-tab-pane label="Magnified" name="magnified">
        <MagnifiedTab />
      </el-tab-pane>
      <el-tab-pane label="Metrics" name="metrics">
        <MetricsTab />
      </el-tab-pane>
      <el-tab-pane label="Spectral Density" name="spectral">
        <SpectralDensityTab />
      </el-tab-pane>
      <el-tab-pane label="Measurement" name="measurement">
        <MeasurementTab />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<style lang="scss" scoped>
.main-panel {
  height: 100%;
  display: flex;
  flex-direction: column;

  &__tabs {
    flex: 1;
    overflow: hidden;

    :deep(.el-tabs__content) {
      overflow-y: auto;
      height: calc(100% - 40px);
    }
  }
}
</style>
