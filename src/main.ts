import { createApp } from "vue";
import { createPinia } from "pinia";
import ElementPlus from "element-plus";
import "element-plus/dist/index.css";

import App from "./App.vue";
import "./styles/global.scss";
import "uno.css";
import "./styles/theme.scss";

// Only apply in development
// if (import.meta.hot) {
//   import('vite-plugin-vue-tracer/client/overlay').then(({ events, state }) => {
//     // Enables the overlay
//     state.isEnabled = true

//     events.on('hover', (info) => {
//       // ...
//     })

//     events.on('click', (info) => {
//       // ...
//       openInEditor(info.fullpath) // 'src/app.vue:10:1'
//       state.isEnabled = false
//     })
//   })
// }

const app = createApp(App);
app.use(createPinia());
app.use(ElementPlus);
app.mount("#app");
