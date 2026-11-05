import { contextBridge } from "electron";

contextBridge.exposeInMainWorld("aura", {
  version: "0.1.0"
});
