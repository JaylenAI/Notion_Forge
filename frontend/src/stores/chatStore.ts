import { create } from "zustand";
import type { Message, GeneratedTemplate } from "../types";
import { useConnectionStore, API_URL } from "./connectionStore";
import { useSettingsStore } from "./settingsStore";

// Re-export for backward compatibility
export { useConnectionStore } from "./connectionStore";
export { useSettingsStore, type PageName } from "./settingsStore";

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

function deriveSessionTitle(messages: readonly Message[]): string {
  const userMsg = messages.find((m) => m.role === "user");
  if (!userMsg) return "New Chat";
  const text = userMsg.content.slice(0, 40);
  return text.length < userMsg.content.length ? `${text}...` : text;
}

interface ChatState {
  messages: Message[];
  isLoading: boolean;
  currentStep: string;
  progressLog: string[];
  generatedTemplates: readonly GeneratedTemplate[];
  sessions: readonly ChatSession[];
  currentSessionId: string | null;
  abortController: AbortController | null;
  pendingApproval: boolean;
  sendMessage: (content: string) => void;
  confirmCreate: () => void;
  cancelCreate: () => void;
  cancelGeneration: () => void;
  clearMessages: () => void;
  saveToLibrary: () => boolean;
  toggleTemplateStar: (id: string) => void;
  deleteTemplate: (id: string) => void;
  saveCurrentSession: () => void;
  loadSession: (sessionId: string) => void;
  deleteSession: (sessionId: string) => void;
  newSession: () => void;
}

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [],
  isLoading: false,
  currentStep: "",
  progressLog: [],
  generatedTemplates: loadTemplates(),
  sessions: loadSessions(),
  currentSessionId: null,
  abortController: null,
  pendingApproval: false,

  sendMessage: (content: string) => {
    const connectionStatus = useConnectionStore.getState().connectionStatus;
    const ws = useConnectionStore.getState().ws;
    const settings = useSettingsStore.getState().settings;

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

  confirmCreate: () => {
    const ws = useConnectionStore.getState().ws;
    if (ws?.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: "confirm_create" }));
    }
    set({ pendingApproval: false, isLoading: true, currentStep: "creating" });
  },

  cancelCreate: () => {
    const ws = useConnectionStore.getState().ws;
    if (ws?.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: "cancel_create" }));
    }
    set({ pendingApproval: false, isLoading: false });
  },

  cancelGeneration: () => {
    const { abortController } = get();
    const ws = useConnectionStore.getState().ws;
    if (abortController) {
      abortController.abort();
    }
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: "cancel" }));
    }
    set({ isLoading: false, currentStep: "", abortController: null });
  },

  clearMessages: () => {
    const { messages, currentSessionId } = get();
    if (messages.length > 0 && !currentSessionId) {
      get().saveCurrentSession();
    }
    set({ messages: [], isLoading: false, currentStep: "", currentSessionId: null });
  },

  saveToLibrary: () => {
    const { messages, generatedTemplates } = get();
    const completeMsg = [...messages].reverse().find(
      (m) => m.metadata?.type === "complete" && m.metadata?.notionUrl
    );
    if (!completeMsg || !completeMsg.metadata?.notionUrl) return false;

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

  /* ─── Session Methods ─── */
  saveCurrentSession: () => {
    const { messages, sessions, currentSessionId } = get();
    if (messages.length === 0) return;

    const now = new Date().toISOString();

    if (currentSessionId) {
      const updated = sessions.map((s) =>
        s.id === currentSessionId
          ? { ...s, messages, updatedAt: now, title: deriveSessionTitle(messages) }
          : s
      );
      saveSessions(updated);
      set({ sessions: updated });
    } else {
      const session: ChatSession = {
        id: `session_${Date.now()}`,
        title: deriveSessionTitle(messages),
        messages,
        createdAt: now,
        updatedAt: now,
      };
      const updated = [session, ...sessions].slice(0, 50);
      saveSessions(updated);
      set({ sessions: updated, currentSessionId: session.id });
    }
  },

  loadSession: (sessionId: string) => {
    const { sessions, messages, currentSessionId } = get();
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
}));
