import { defineConfig } from "vite";
import path from "path";
import pkg from "./package.json" with { type: "json" };

export default defineConfig({
  build: {
    sourcemap: true,
    lib: {
      entry: path.resolve(import.meta.dirname, "src/index.ts"),
      name: "discography",
      fileName: (format) => `index.${format}.js`,
    },
    rolldownOptions: {
      external: pkg.devDependencies ? Object.keys(pkg.devDependencies) : [],
      output: {
        exports: "named",
        strict: false,
      },
    },
  },
});
