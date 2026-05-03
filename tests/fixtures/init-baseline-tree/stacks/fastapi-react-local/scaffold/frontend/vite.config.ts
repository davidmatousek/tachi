/**
 * Vite configuration for the React frontend.
 *
 * Plugins:
 * - @vitejs/plugin-react: React Fast Refresh and JSX transform
 * - @tailwindcss/vite: Tailwind CSS v4 first-party Vite integration
 *
 * Path alias: "@/" resolves to "src/" for clean imports.
 * Test config: Vitest with jsdom environment and global test APIs.
 */
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import path from "node:path";

export default defineConfig({
  plugins: [react(), tailwindcss()],

  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },

  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: ["./tests/setup.ts"],
  },
});
