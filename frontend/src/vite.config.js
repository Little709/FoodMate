import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    hmr: {
      overlay: false, // Disable error overlay for a cleaner debugging experience
    },
  },
  esbuild: {
    jsxInject: `import React from 'react'`, // Ensures React is globally available for JSX
  },
});
