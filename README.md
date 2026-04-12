---
title: Relay Lens
emoji: 🔬
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
license: agpl-3.0
short_description: Hyperspectral Image Reconstruction Visualization
---

# Relay Lens

Hyperspectral Image (HSI) reconstruction visualization tool.

## Features

- Load `.mat` files containing HSI cubes and interactively explore:
  - **RGB** rendering from spectral data
  - **Single-channel** pseudo-colored visualization
  - **Magnified** ROI inset overlays
  - **Metrics** (PSNR / SSIM) line charts
  - **Spectral Density** curves
  - **CASSI Measurement** simulation with coded aperture masks

### Screenshots

<details>
<summary>Click to expand</summary>

<img width="1680" height="1204" alt="Image" src="https://github.com/user-attachments/assets/faca3fd8-26b9-450f-a1ea-7bae04eb60f4" />

<img width="1680" height="1204" alt="Image" src="https://github.com/user-attachments/assets/056e9998-2189-40b0-a7e9-3c5e4bda592f" />

<img width="1678" height="1202" alt="Image" src="https://github.com/user-attachments/assets/16b23118-0ccc-4ce8-9d2e-9b91a081d52c" />

<img width="1681" height="1203" alt="Image" src="https://github.com/user-attachments/assets/87b3ac97-95bf-4e23-8241-b7202f09b4e3" />

</details>

## Usage

### In a huggingface space

1. Open [project huggingface space](https://huggingface.co/spaces/markchen9804/relay-lens).
2. Click on the top-left stash area to select `.mat` files, or drag and drop `.mat` files into the stash area.
3. Click "Upload" button. Your file will not be used for any other purpose.
4. On the left sidebar, select a key and start exploring.
5. Switch between tabs to explore RGB, single-channel, metrics, spectral density (WIP), and upload additional `.mat` mask file to simulate a CASSI measurement image.

### On local machine

> [!WARNING]
> Be sure to install a node version between 20.x and 24.x. This application is unlikely to support 25.x.

1. Install [node](https://nodejs.org/en/download) and [python](https://www.python.org/downloads/) on your machine.
2. Install [pnpm](https://pnpm.io/installation) and [uv](https://docs.astral.sh/uv/getting-started/installation/) on your machine.
3. Clone the repository.
4. In the root directory, run `pnpm i` to install frontend dependencies.
5. Run `uv sync` to install backend dependencies.
6. Run `pnpm dev` to start the application.

The only difference between local and huggingface environment is that you can put `.mat` file(s) in the `input` folder to perform a quick local folder scan to automatically load all files.

## Local Development

Please refer to [Usage on local machine](#on-local-machine) for detailed instructions. `relay-lens` requires Python 3.10+ and Node.js 20+.
