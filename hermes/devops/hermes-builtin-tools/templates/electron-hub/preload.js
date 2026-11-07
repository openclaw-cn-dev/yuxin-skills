// preload.js — contextIsolation 安全桥
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('hermes', {
  chat: payload => ipcRenderer.invoke('chat', payload),
  getConfig: () => ipcRenderer.invoke('get-config')
});
