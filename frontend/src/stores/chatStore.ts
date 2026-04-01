import { create } from "zustand";
import type { Message, Settings, ConnectionStatus, AiModel, GeneratedTemplate } from "../types";

const WS_URL = import.meta.env.VITE_WS_URL ?? "ws://localhost:9500";
const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:9500";

const SETTINGS_KEY = "notionforge_settings";
const TEMPLATES_KEY = "notionforge_templates";

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

function loadTemplates(): GeneratedTemplate[] {
  try {
    const raw = localStorage.getItem(TEMPLATES_KEY);
    if (raw) return JSON.parse(raw);
  } catch {
    // ignore
  }
  return [];
}

function saveTemplates(templates: readonly GeneratedTemplate[]): void {
  localStorage.setItem(TEMPLATES_KEY, JSON.stringify(templates));
}

export type PageName = "dashboard" | "library" | "integrations" | "profile" | "support";

interface ChatState {
  messages: Message[];
  isLoading: boolean;
  connectionStatus: ConnectionStatus;
  ws: WebSocket | null;
  settings: Settings;
  settingsOpen: boolean;
  currentStep: string;
  currentPage: PageName;
  generatedTemplates: readonly GeneratedTemplate[];
  connectionTested: boolean;
  aiProvider: string;
  aiModels: AiModel[];
  aiDetecting: boolean;
  connect: () => void;
  disconnect: () => void;
  sendMessage: (content: string) => void;
  updateSettings: (settings: Settings) => void;
  toggleSettings: () => void;
  clearMessages: () => void;
  setPage: (page: PageName) => void;
  toggleTemplateStar: (id: string) => void;
  deleteTemplate: (id: string) => void;
  setConnectionTested: (tested: boolean) => void;
  detectProvider: (apiKey: string) => Promise<void>;
}

function addTemplateFromMessage(state: ChatState, msg: Message): readonly GeneratedTemplate[] {
  if (msg.metadata?.type !== "complete" || !msg.metadata?.notionUrl) return state.generatedTemplates;

  const blueprint = state.messages.find((m) => m.metadata?.blueprint)?.metadata?.blueprint as Record<string, unknown> | undefined;
  const meta = blueprint?.metadata as Record<string, unknown> | undefined;

  const template: GeneratedTemplate = {
    id: `tpl_${Date.now()}`,
    title: (meta?.title as string) ?? "Untitled Template",
    description: msg.content.split("\n")[0] ?? "",
    skill: (meta?.template_type as string) ?? "custom",
    date: new Date().toISOString().slice(0, 10),
    starred: false,
    notionUrl: msg.metadata.notionUrl,
    blueprint: blueprint,
  };

  const updated = [template, ...state.generatedTemplates];
  saveTemplates(updated);
  return updated;
}

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [],
  isLoading: false,
  connectionStatus: "disconnected",
  ws: null,
  settings: loadSettings(),
  settingsOpen: false,
  currentStep: "",
  currentPage: "dashboard",
  connectionTested: false,
  aiProvider: "",
  aiModels: [],
  aiDetecting: false,
  generatedTemplates: loadTemplates(),

  connect: () => {
    const { ws: existing } = get();
    if (existing && existing.readyState === WebSocket.OPEN) return;

    set({ connectionStatus: "connecting" });

    try {
      const ws = new WebSocket(`${WS_URL}/ws/chat`);

      ws.onopen = () => {
        const { settings } = get();
        set({ connectionStatus: "connected", ws });
        ws.send(
          JSON.stringify({
            type: "init",
            notion_token: settings.notionKey,
            parent_page_id: settings.pageId,
            ai_key: settings.aiKey,
            ai_model: settings.aiModel,
          })
        );
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          const msg: Message = {
            id: crypto.randomUUID(),
            role: "assistant",
            content: data.content ?? data.message ?? "",
            timestamp: new Date(),
            metadata: {
              type: data.type,
              notionUrl: data.result?.main_url,
              blueprint: data.blueprint,
              step: data.step,
            },
          };

          set((state) => {
            const newTemplates = addTemplateFromMessage(state, msg);
            return {
              messages: [...state.messages, msg],
              isLoading: data.type === "progress",
              currentStep: data.type === "progress" ? (data.step ?? "") : "",
              generatedTemplates: newTemplates,
            };
          });
        } catch {
          // ignore parse errors
        }
      };

      ws.onclose = () => set({ connectionStatus: "disconnected", ws: null });
      ws.onerror = () => set({ connectionStatus: "disconnected" });
    } catch {
      set({ connectionStatus: "disconnected" });
    }
  },

  disconnect: () => {
    get().ws?.close();
    set({ ws: null, connectionStatus: "disconnected" });
  },

  sendMessage: (content: string) => {
    const { ws, connectionStatus, settings } = get();

    const userMsg: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content,
      timestamp: new Date(),
    };
    set((state) => ({
      messages: [...state.messages, userMsg],
      isLoading: true,
      currentStep: "sending",
    }));

    if (ws && connectionStatus === "connected") {
      ws.send(JSON.stringify({ type: "message", content }));
    } else {
      fetch(`${API_URL}/api/templates/preview`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(settings.notionKey
            ? { "X-Notion-Token": settings.notionKey }
            : {}),
        },
        body: JSON.stringify({
          prompt: content,
          parent_page_id: settings.pageId,
        }),
      })
        .then((r) => r.json())
        .then((data) => {
          const meta = data.blueprint?.metadata;
          const aiMsg: Message = {
            id: crypto.randomUUID(),
            role: "assistant",
            content: meta
              ? `${meta.title} (${meta.template_type})\nPreview generated successfully.`
              : "Request processed.",
            timestamp: new Date(),
            metadata: {
              type: "blueprint_preview",
              blueprint: data.blueprint,
            },
          };
          set((state) => ({
            messages: [...state.messages, aiMsg],
            isLoading: false,
            currentStep: "",
          }));
        })
        .catch(() => {
          set((state) => ({
            messages: [
              ...state.messages,
              {
                id: crypto.randomUUID(),
                role: "assistant" as const,
                content: "Failed to connect to server. Please check your connection settings.",
                timestamp: new Date(),
                metadata: { type: "error" },
              },
            ],
            isLoading: false,
            currentStep: "",
          }));
        });
    }
  },

  updateSettings: (newSettings: Settings) => {
    saveSettings(newSettings);
    set({ settings: newSettings });

    const { ws } = get();
    if (ws) {
      ws.close();
    }
    setTimeout(() => get().connect(), 300);
  },

  toggleSettings: () => {
    set((state) => ({ settingsOpen: !state.settingsOpen }));
  },

  clearMessages: () => {
    set({ messages: [], isLoading: false, currentStep: "" });
  },

  setPage: (page: PageName) => {
    set({ currentPage: page });
  },

  toggleTemplateStar: (id: string) => {
    set((state) => {
      const updated = state.generatedTemplates.map((t) =>
        t.id === id ? { ...t, starred: !t.starred } : t
      );
      saveTemplates(updated);
      return { generatedTemplates: updated };
    });
  },

  deleteTemplate: (id: string) => {
    set((state) => {
      const updated = state.generatedTemplates.filter((t) => t.id !== id);
      saveTemplates(updated);
      return { generatedTemplates: updated };
    });
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
}));
