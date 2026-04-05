/**
 * API client for Relay-Lens backend.
 * Plain fetch wrappers - no external HTTP library needed.
 */

const BASE = "/api";

// -- Types --

export interface KeyInfo {
  name: string;
  shape: number[];
  dtype: string;
  dataType: "hsi_cube_batch" | "hsi_cube" | "metric_array" | "image_2d" | "unknown";
}

export interface FileEntry {
  fileId: string;
  filename: string;
  keys: KeyInfo[];
}

// -- File Management --

export async function uploadFiles(files: File[]): Promise<FileEntry[]> {
  const form = new FormData();
  for (const f of files) form.append("files", f);
  const res = await fetch(`${BASE}/files/upload`, { method: "POST", body: form });
  if (!res.ok) throw new Error(`Upload failed: ${res.statusText}`);
  const data = await res.json();
  return data.files;
}

export async function scanLocalFiles(): Promise<FileEntry[]> {
  const res = await fetch(`${BASE}/files/scan-local`, { method: "POST" });
  if (!res.ok) throw new Error(`Scan failed: ${res.statusText}`);
  const data = await res.json();
  return data.files;
}

export async function getFiles(): Promise<FileEntry[]> {
  const res = await fetch(`${BASE}/files`);
  if (!res.ok) throw new Error(`List failed: ${res.statusText}`);
  const data = await res.json();
  return data.files;
}

export async function getCommonKeys(): Promise<KeyInfo[]> {
  const res = await fetch(`${BASE}/files/common-keys`);
  if (!res.ok) throw new Error(`Common keys failed: ${res.statusText}`);
  const data = await res.json();
  return data.commonKeys;
}

export async function getFileInfo(fileId: string): Promise<unknown> {
  const res = await fetch(`${BASE}/files/${fileId}/info`);
  if (!res.ok) throw new Error(`File info failed: ${res.statusText}`);
  const data = await res.json();
  return data.structure;
}

export async function deleteFile(fileId: string): Promise<void> {
  const res = await fetch(`${BASE}/files/${fileId}`, { method: "DELETE" });
  if (!res.ok) throw new Error(`Delete failed: ${res.statusText}`);
}

// -- Visualization URL builders --

export function vizUrl(type: string, params: Record<string, string | number>): string {
  const query = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    query.set(k, String(v));
  }
  return `${BASE}/viz/${type}?${query.toString()}`;
}

// -- Helpers --

export function getSceneCount(keyInfo: KeyInfo): number {
  if (keyInfo.dataType === "hsi_cube_batch") return keyInfo.shape[0];
  if (keyInfo.dataType === "hsi_cube") return 1;
  return 0;
}

export function formatShape(shape: number[]): string {
  return `(${shape.join(", ")})`;
}

export function dataTypeLabel(dt: string): string {
  const labels: Record<string, string> = {
    hsi_cube_batch: "HSI",
    hsi_cube: "HSI",
    metric_array: "1D",
    image_2d: "2D",
    unknown: "?",
  };
  return labels[dt] ?? dt;
}

// -- Mask management --

export interface MaskStatus {
  loaded: boolean;
  filename?: string;
  shape?: number[];
}

export async function uploadMask(file: File): Promise<MaskStatus> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${BASE}/files/upload-mask`, { method: "POST", body: form });
  if (!res.ok) throw new Error(`Mask upload failed: ${res.statusText}`);
  return res.json();
}

export async function scanMask(): Promise<MaskStatus> {
  const res = await fetch(`${BASE}/files/scan-mask`, { method: "POST" });
  if (!res.ok) throw new Error(`Mask scan failed: ${res.statusText}`);
  return res.json();
}

export async function getMaskStatus(): Promise<MaskStatus> {
  const res = await fetch(`${BASE}/files/mask-status`);
  if (!res.ok) throw new Error(`Mask status failed: ${res.statusText}`);
  return res.json();
}
