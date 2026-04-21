import { create } from "zustand";
import type { Settings, AiModel } from "../types";
import { useConnectionStore } from "./connectionStore";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:9500";
const SETTINGS_KEY = "notionforge_settings";

export type PageName = "dashboard" | "library" | "integrations" | "profile" | "support";

function loadSettings(): Settings {
  try {
    const raw = localStorage.getItem(SETTINGS_KEY);
    if (raw) {
      const parsed = JSON.parse(raw);
      return {
        notionKey: parsed.notionKey ?? "",
        pageId: parsed.pageId ?? "",
        aiKey: parsed.aiKey ?? "",
        aiModel: parsed.aiModel ?? "",
      };
    }
  } catch {
    // ignore
  }
  return { notionKey: "", pageId: "", aiKey: "", aiModel: "" };
}

function saveSettings(settings: Settings): void {
  localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings));
}

interface SettingsState {
  settings: Settings;
  settingsOpen: boolean;
  currentPage: PageName;
  connectionTested: boolean;
  aiProvider: string;
  aiModels: AiModel[];
  aiDetecting: boolean;
  copilotStatus: { available: boolean; model: string; models: AiModel[] } | null;
  complexity: "simple" | "standard" | "advanced";
  language: "ko" | "en" | "ja";
  updateSettings: (settings: Settings) => void;
  toggleSettings: () => void;
  setPage: (page: PageName) => void;
  setConnectionTested: (tested: boolean) => void;
  detectProvider: (apiKey: string) => Promise<void>;
  fetchCopilotStatus: () => Promise<void>;
  setCopilotModel: (modelId: string) => Promise<void>;
  setComplexity: (c: "simple" | "standard" | "advanced") => void;
  setLanguage: (l: "ko" | "en" | "ja") => void;
}

export const useSettingsStore = create<SettingsState>((set, get) => ({
  settings: loadSettings(),
  settingsOpen: false,
  currentPage: "dashboard",
  connectionTested: false,
  aiProvider: "",
  aiModels: [],
  aiDetecting: false,
  copilotStatus: null,
  complexity: "standard",
  language: "ko",

  updateSettings: (newSettings: Settings) => {
    saveSettings(newSettings);
    set({ settings: newSettings });

    // Reconnect with new settings
    const connStore = useConnectionStore.getState();
    connStore.disconnect();
    setTimeout(() => useConnectionStore.getState().connect(), 300);
  },

  toggleSettings: () => {
    set((state) => ({ settingsOpen: !state.settingsOpen }));
  },

  setPage: (page: PageName) => {
    set({ currentPage: page });
  },

  setConnectionTested: (tested: boolean) => {
    set({ connectionTested: tested });
  },

  detectProvider: async (apiKey: string) => {
    if (!apiKey.trim()) return;
    set({ aiDetecting: true, aiModels: [], aiProvider: "" });
    try {
      const resp = await fetch(`${API_URL}/api/templates/ai/detect-provider`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ api_key: apiKey }),
      });
      const data = await resp.json();
      set({
        aiProvider: data.provider ?? "",
        aiModels: data.models ?? [],
      });
    } catch {
      set({ aiProvider: "", aiModels: [] });
    } finally {
      set({ aiDetecting: false });
    }
  },

  fetchCopilotStatus: async () => {
    try {
      const resp = await fetch(`${API_URL}/api/templates/ai/copilot-status`);
      const data = await resp.json();
      set({
        copilotStatus: {
          available: data.available ?? false,
          model: data.current_model ?? "gpt-4.1",
          models: (data.models ?? []).map((m: { id: string; name: string }) => ({
            id: m.id,
            name: m.name,
          })),
        },
      });
    } catch {
      set({ copilotStatus: null });
    }
  },

  setCopilotModel: async (modelId: string) => {
    try {
      await fetch(`${API_URL}/api/templates/ai/copilot-model`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ model: modelId }),
      });
      const prev = get().copilotStatus;
      if (prev) {
        set({ copilotStatus: { ...prev, model: modelId } });
      }
    } catch {
      // ignore
    }
  },

  setComplexity: (c) => {
    set({ complexity: c });
    const ws = useConnectionStore.getState().ws;
    if (ws?.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: "set_complexity", complexity: c }));
    }
  },

  setLanguage: (l) => {
    set({ language: l });
    const ws = useConnectionStore.getState().ws;
    if (ws?.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: "set_language", language: l }));
    }
  },
}));
