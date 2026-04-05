<script setup lang="ts">
import { computed } from "vue";
import { useFileStore } from "@/stores/fileStore";
import { formatShape, dataTypeLabel } from "@/api/client";

const fileStore = useFileStore();

interface TreeNode {
  id: string;
  label: string;
  isLeaf: boolean;
  dataType?: string;
  shape?: number[];
  children?: TreeNode[];
}

const treeData = computed<TreeNode[]>(() => {
  return fileStore.filesArray.map((file) => ({
    id: file.fileId,
    label: file.filename,
    isLeaf: false,
    children: file.keys.map((key) => ({
      id: `${file.fileId}:${key.name}`,
      label: key.name,
      isLeaf: true,
      dataType: key.dataType,
      shape: key.shape,
    })),
  }));
});

function handleNodeClick(data: TreeNode) {
  if (data.isLeaf && data.dataType && data.dataType !== "unknown") {
    fileStore.selectedKey = data.label;
  }
}

function removeFile(fileId: string, event: Event) {
  event.stopPropagation();
  fileStore.removeFile(fileId);
}

function clearAll() {
  const ids = fileStore.filesArray.map((f) => f.fileId);
  for (const id of ids) {
    fileStore.removeFile(id);
  }
}
</script>

<template>
  <div class="file-tree">
    <div class="tree-header">
      <span class="tree-label">Files ({{ fileStore.filesArray.length }})</span>
    </div>

    <el-tree
      v-if="treeData.length > 0"
      :data="treeData"
      node-key="id"
      default-expand-all
      :expand-on-click-node="false"
      @node-click="handleNodeClick"
    >
      <template #default="{ data }">
        <span class="tree-node">
          <span class="tree-node-label">{{ data.label }}</span>
          <template v-if="data.isLeaf">
            <el-tag size="small" :type="data.dataType === 'unknown' ? 'info' : ''" effect="plain">
              {{ dataTypeLabel(data.dataType) }}
            </el-tag>
            <span class="tree-node-shape">{{ formatShape(data.shape) }}</span>
          </template>
          <el-button
            v-else
            class="delete-btn"
            type="danger"
            plain
            size="small"
            @click="removeFile(data.id, $event)"
          >
            Remove
          </el-button>
        </span>
      </template>
    </el-tree>

    <el-empty v-else description="No files loaded" :image-size="48" />

    <el-button
      v-if="fileStore.filesArray.length > 0"
      type="danger"
      plain
      size="small"
      class="clear-all-btn"
      @click="clearAll"
    >
      Clear All
    </el-button>
  </div>
</template>

<style lang="scss" scoped>
:deep(.el-tree-node__content) {
  width: 100%;
}

.tree-header {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.tree-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--el-text-color-regular);
}

.tree-node {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  width: 100%;
}

.tree-node-label {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tree-node-shape {
  font-size: 11px;
  color: var(--el-text-color-placeholder);
  font-family: monospace;
}

.delete-btn {
  margin-left: auto;
  margin-right: 4px;
  border: none;
  background-color: transparent;

  &:hover {
    background-color: var(--el-button-hover-bg-color);
  }
}

.clear-all-btn {
  margin-top: 12px;
  width: 100%;
}
</style>
