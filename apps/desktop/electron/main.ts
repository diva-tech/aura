import { app, BrowserWindow, shell } from "electron";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const isDevelopment = Boolean(process.env.VITE_DEV_SERVER_URL);

const createWindow = async (): Promise<void> => {
  const window = new BrowserWindow({
    width: 1440,
    height: 900,
    minWidth: 1200,
    minHeight: 760,
    backgroundColor: "#09090b",
    show: false,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
      devTools: isDevelopment
    }
  });

  window.once("ready-to-show", () => {
    window.show();
  });

  window.webContents.setWindowOpenHandler(({ url }) => {
    void shell.openExternal(url);
    return { action: "deny" };
  });

  window.webContents.on("will-navigate", (event, url) => {
    if (isDevelopment && process.env.VITE_DEV_SERVER_URL !== undefined) {
      const allowedOrigin = new URL(process.env.VITE_DEV_SERVER_URL).origin;
      if (new URL(url).origin !== allowedOrigin) {
        event.preventDefault();
      }
      return;
    }

    const filePath = path.normalize(url.replace("file://", ""));
    const appDistPath = path.normalize(path.join(__dirname, "../dist/index.html"));
    if (filePath !== appDistPath) {
      event.preventDefault();
    }
  });

  if (isDevelopment && process.env.VITE_DEV_SERVER_URL !== undefined) {
    await window.loadURL(process.env.VITE_DEV_SERVER_URL);
    return;
  }

  await window.loadFile(path.join(__dirname, "../dist/index.html"));
};

void app.whenReady().then(async () => {
  await createWindow();

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      void createWindow();
    }
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});
