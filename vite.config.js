import { defineConfig } from "vite";
import path from "path";
import pkg from "./package.json";

export default defineConfig({
  build: {
    lib: {
      entry: path.resolve(__dirname, "src/index.ts"),
      name: "discography",
      fileName: (format) => `discography.${format}.js`,
    },
    rollupOptions: {
      external: pkg.devDependencies ? Object.keys(pkg.devDependencies) : [],
      output: {
        exports: "named",
        sourcemap: true,
        strict: false,
      },
    },
  },
});
