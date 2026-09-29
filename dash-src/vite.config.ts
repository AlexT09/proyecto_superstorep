import { defineConfig } from "vite";
import tsConfigPaths from "vite-tsconfig-paths";
import tailwindcss from "@tailwindcss/vite";
import { tanstackStart } from "@tanstack/react-start/plugin/vite";
import viteReact from "@vitejs/plugin-react";
import { nitro } from "nitro/vite";

export default defineConfig({
  // Puerto fijo para que la pestaña "Dashboard" de la app de Dash (tabs/dashboard.py)
  // siempre lo encuentre en http://localhost:5173/, tanto en dev como en preview.
  server: { port: 5173 },
  preview: { port: 5173 },
  plugins: [
    tsConfigPaths({ projects: ["./tsconfig.json"] }),
    tailwindcss(),
    tanstackStart(),
    viteReact(),
    // Empaqueta el servidor SSR (incl. /api/chat) como un servidor Node
    // standalone en .output/server/index.mjs.
    nitro({ preset: "node-server" }),
  ],
});
