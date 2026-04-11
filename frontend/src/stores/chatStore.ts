import { create } from "zustand";
import type { Message, Settings, ConnectionStatus, AiModel, GeneratedTemplate } from "../types";

const WS_URL = import.meta.env.VITE_WS_URL ?? "ws://localhost:9500";
const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:9500";

const SETTINGS_KEY = "notionforge_settings";
const TEMPLATES_KEY = "notionforge_templates";
const SESSIONS_KEY = "notionforge_sessions";

/* ─── Chat Session ─── */
export interface ChatSession {
  readonly id: string;
  readonly title: string;
  readonly messages: readonly Message[];
  readonly createdAt: string;
  readonly updatedAt: string;
}

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

function loadSessions(): ChatSession[] {
  try {
    const raw = localStorage.getItem(SESSIONS_KEY);
    if (raw) return JSON.parse(raw);
  } catch {
    // ignore
  }
  return [];
}

function saveSessions(sessions: readonly ChatSession[]): void {
  localStorage.setItem(SESSIONS_KEY, JSON.stringify(sessions));
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
  progressLog: string[];
  currentPage: PageName;
  generatedTemplates: readonly GeneratedTemplate[];
  connectionTested: boolean;
  aiProvider: string;
  aiModels: AiModel[];
  aiDetecting: boolean;
  /* Copilot */
  copilotStatus: { available: boolean; model: string; models: AiModel[] } | null;
  /* Session management */
  sessions: readonly ChatSession[];
  currentSessionId: string | null;
  /* Abort controller for cancel */
  abortController: AbortController | null;
  /* Complexity & Language */
  complexity: "simple" | "standard" | "advanced";
  language: "ko" | "en" | "ja";
  connect: () => void;
  disconnect: () => void;
  sendMessage: (content: string) => void;
  cancelGeneration: () => void;
  updateSettings: (settings: Settings) => void;
  toggleSettings: () => void;
  clearMessages: () => void;
  setPage: (page: PageName) => void;
  toggleTemplateStar: (id: string) => void;
  deleteTemplate: (id: string) => void;
  setConnectionTested: (tested: boolean) => void;
  detectProvider: (apiKey: string) => Promise<void>;
  fetchCopilotStatus: () => Promise<void>;
  setCopilotModel: (modelId: string) => Promise<void>;
  /* Library save */
  saveToLibrary: () => boolean;
  /* Session methods */
  saveCurrentSession: () => void;
  loadSession: (sessionId: string) => void;
  deleteSession: (sessionId: string) => void;
  newSession: () => void;
  /* Complexity & Language setters */
  setComplexity: (c: "simple" | "standard" | "advanced") => void;
  setLanguage: (l: "ko" | "en" | "ja") => void;
}

function deriveSessionTitle(messages: readonly Message[]): string {
  const userMsg = messages.find((m) => m.role === "user");
  if (!userMsg) return "New Chat";
  const text = userMsg.content.slice(0, 40);
  return text.length < userMsg.content.length ? `${text}...` : text;
}

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [],
  isLoading: false,
  connectionStatus: "disconnected",
  ws: null,
  settings: loadSettings(),
  settingsOpen: false,
  currentStep: "",
  progressLog: [],
  currentPage: "dashboard",
  connectionTested: false,
  aiProvider: "",
  aiModels: [],
  aiDetecting: false,
  copilotStatus: null,
  generatedTemplates: loadTemplates(),
  sessions: loadSessions(),
  currentSessionId: null,
  abortController: null,
  complexity: "standard",
  language: "ko",

  connect: () => {
    const { ws: existing, connectionStatus } = get();
    if (existing && (existing.readyState === WebSocket.OPEN || existing.readyState === WebSocket.CONNECTING)) return;
    if (connectionStatus === "connecting") return;

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
          const eventType = data.type ?? "";

          // progress 이벤트: 실시간 로그 스트림 (messages에는 안 추가)
          if (eventType === "progress") {
            const logMsg = data.message ?? data.step ?? "";
            set((state) => ({
              isLoading: true,
              currentStep: data.step ?? "",
              progressLog: logMsg ? [...state.progressLog.slice(-15), logMsg] : state.progressLog,
            }));
            return;
          }

          // system 이벤트: 연결 완료 메시지만 추가
          if (eventType === "system") {
            const msg: Message = {
              id: crypto.randomUUID(),
              role: "assistant",
              content: data.content ?? data.message ?? "",
              timestamp: new Date(),
              metadata: { type: "system" },
            };
            set((state) => ({
              messages: [...state.messages, msg],
              isLoading: false,
            }));
            return;
          }

          // complete, error, blueprint_preview 등: 메시지에 추가
          const msg: Message = {
            id: crypto.randomUUID(),
            role: "assistant",
            content: data.content ?? data.message ?? "",
            timestamp: new Date(),
            metadata: {
              type: eventType,
              notionUrl: data.result?.main_url,
              blueprint: data.blueprint,
              step: data.step,
            },
          };

          set((state) => ({
            messages: [...state.messages, msg],
            isLoading: false,
            currentStep: "",
            progressLog: eventType === "complete" || eventType === "error" ? [] : state.progressLog,
          }));
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
      progressLog: [],
    }));

    if (ws && connectionStatus === "connected") {
      ws.send(JSON.stringify({ type: "message", content }));
    } else {
      const controller = new AbortController();
      set({ abortController: controller });

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
        signal: controller.signal,
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
            abortController: null,
          }));
        })
        .catch((err) => {
          if (err.name === "AbortError") {
            set((state) => ({
              messages: [
                ...state.messages,
                {
                  id: crypto.randomUUID(),
                  role: "assistant" as const,
                  content: "Generation cancelled.",
                  timestamp: new Date(),
                  metadata: { type: "cancelled" },
                },
              ],
              isLoading: false,
              currentStep: "",
              abortController: null,
            }));
            return;
          }
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
            abortController: null,
          }));
        });
    }
  },

  cancelGeneration: () => {
    const { abortController, ws } = get();
    if (abortController) {
      abortController.abort();
    }
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: "cancel" }));
    }
    set({ isLoading: false, currentStep: "", abortController: null });
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
    const { messages, currentSessionId } = get();
    // Auto-save current session before clearing
    if (messages.length > 0 && !currentSessionId) {
      get().saveCurrentSession();
    }
    set({ messages: [], isLoading: false, currentStep: "", currentSessionId: null });
  },

  setPage: (page: PageName) => {
    set({ currentPage: page });
  },

  saveToLibrary: () => {
    const { messages, generatedTemplates } = get();
    const completeMsg = [...messages].reverse().find(
      (m) => m.metadata?.type === "complete" && m.metadata?.notionUrl
    );
    if (!completeMsg || !completeMsg.metadata?.notionUrl) return false;

    // Check if already saved
    const url = completeMsg.metadata.notionUrl;
    if (generatedTemplates.some((t) => t.notionUrl === url)) return false;

    const blueprint = messages.find((m) => m.metadata?.blueprint)?.metadata?.blueprint as Record<string, unknown> | undefined;
    const meta = blueprint?.metadata as Record<string, unknown> | undefined;

    const template: GeneratedTemplate = {
      id: `tpl_${Date.now()}`,
      title: (meta?.title as string) ?? "Untitled Template",
      description: completeMsg.content.split("\n")[0] ?? "",
      skill: (meta?.template_type as string) ?? "custom",
      date: new Date().toISOString().slice(0, 10),
      starred: false,
      notionUrl: url,
      blueprint: blueprint,
    };

    const updated = [template, ...generatedTemplates];
    saveTemplates(updated);
    set({ generatedTemplates: updated });
    return true;
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

  /* ─── Session Methods ─── */
  saveCurrentSession: () => {
    const { messages, sessions, currentSessionId } = get();
    if (messages.length === 0) return;

    const now = new Date().toISOString();

    if (currentSessionId) {
      // Update existing session
      const updated = sessions.map((s) =>
        s.id === currentSessionId
          ? { ...s, messages, updatedAt: now, title: deriveSessionTitle(messages) }
          : s
      );
      saveSessions(updated);
      set({ sessions: updated });
    } else {
      // Create new session
      const session: ChatSession = {
        id: `session_${Date.now()}`,
        title: deriveSessionTitle(messages),
        messages,
        createdAt: now,
        updatedAt: now,
      };
      const updated = [session, ...sessions].slice(0, 50); // Keep max 50 sessions
      saveSessions(updated);
      set({ sessions: updated, currentSessionId: session.id });
    }
  },

  loadSession: (sessionId: string) => {
    const { sessions, messages, currentSessionId } = get();
    // Auto-save current before loading another
    if (messages.length > 0 && !currentSessionId) {
      get().saveCurrentSession();
    }
    const session = sessions.find((s) => s.id === sessionId);
    if (session) {
      set({
        messages: [...session.messages],
        currentSessionId: sessionId,
        isLoading: false,
        currentStep: "",
      });
    }
  },

  deleteSession: (sessionId: string) => {
    set((state) => {
      const updated = state.sessions.filter((s) => s.id !== sessionId);
      saveSessions(updated);
      return {
        sessions: updated,
        currentSessionId: state.currentSessionId === sessionId ? null : state.currentSessionId,
      };
    });
  },

  newSession: () => {
    const { messages } = get();
    if (messages.length > 0) {
      get().saveCurrentSession();
    }
    set({ messages: [], isLoading: false, currentStep: "", currentSessionId: null });
  },

  setComplexity: (c) => {
    set({ complexity: c });
    const { ws } = get();
    if (ws?.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: "set_complexity", complexity: c }));
    }
  },

  setLanguage: (l) => {
    set({ language: l });
    const { ws } = get();
    if (ws?.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: "set_language", language: l }));
    }
  },
}));
