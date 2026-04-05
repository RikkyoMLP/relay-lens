<script setup lang="ts">
// Spectral density tab - multi-file curve overlay
// Full implementation planned for Phase 4
</script>

<template>
  <div class="spectral-placeholder">
    <el-empty description="Spectral Density - coming in Phase 4" :image-size="64">
      <template #description>
        <p>Multi-file spectral density curve overlay</p>
        <p style="font-size: 12px; color: var(--el-text-color-placeholder)">
          Select ROI region, choose multiple file/key combinations, customize curve labels
        </p>
      </template>
    </el-empty>
  </div>
</template>
