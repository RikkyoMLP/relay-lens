<script setup lang="ts">
defineProps<{
  imageUrls: string[];
  label?: string;
}>();
</script>

<template>
  <div>
    <div v-if="label" class="file-section-header">{{ label }}</div>
    <div class="scene-grid">
      <div v-for="(url, i) in imageUrls" :key="i" class="scene-cell">
        <img :src="url" loading="lazy" :alt="`Scene ${i}`" />
      </div>
    </div>
  </div>
</template>
