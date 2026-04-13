import { defineConfig, presetIcons, transformerDirectives, transformerVariantGroup } from "unocss";
import presetWind3 from "@unocss/preset-wind3";

export default defineConfig({
  safelist: ["i-mdi-github"],
  rules: [],
  presets: [
    presetWind3(),
    presetIcons({
      scale: 1.2,
      warn: true,
      unit: "em",
    }),
  ],
  transformers: [transformerDirectives(), transformerVariantGroup()],
  theme: {
    breakpoints: {
      xs: "375px",
      sm: "640px",
      md: "768px",
      lg: "1024px",
      xl: "1280px",
    },
  },
});
