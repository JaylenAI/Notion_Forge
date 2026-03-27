import { create } from "zustand";
import type { Message, Settings, ConnectionStatus } from "../types";

const WS_URL = import.meta.env.VITE_WS_URL ?? "ws://localhost:9500";
const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:9500";

const SETTINGS_KEY = "notionforge_settings";

function loadSettings(): Settings {
  try {
    const raw = localStorage.getItem(SETTINGS_KEY);
    if (raw) {
      const parsed = JSON.parse(raw);
      return {
        notionKey: parsed.notionKey ?? "",
        pageId: parsed.pageId ?? "",
      };
    }
  } catch {
    // ignore
  }
  return { notionKey: "", pageId: "" };
}

function saveSettings(settings: Settings): void {
  localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings));
}

interface ChatState {
  messages: Message[];
  isLoading: boolean;
  connectionStatus: ConnectionStatus;
  ws: WebSocket | null;
  settings: Settings;
  settingsOpen: boolean;
  currentStep: string;
  connect: () => void;
  disconnect: () => void;
  sendMessage: (content: string) => void;
  updateSettings: (settings: Settings) => void;
  toggleSettings: () => void;
  clearMessages: () => void;
}

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [],
  isLoading: false,
  connectionStatus: "disconnected",
  ws: null,
  settings: loadSettings(),
  settingsOpen: false,
  currentStep: "",

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

          set((state) => ({
            messages: [...state.messages, msg],
            isLoading: data.type === "progress",
            currentStep: data.type === "progress" ? (data.step ?? "") : "",
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
    }));

    if (ws && connectionStatus === "connected") {
      ws.send(JSON.stringify({ type: "message", content }));
    } else {
      // WebSocket 없으면 REST API로 폴백
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
              ? `📄 ${meta.title} (${meta.template_type})\n🎨 색상: ${meta.color_theme}\n\n구조 미리보기가 생성되었습니다.`
              : "요청을 처리했습니다.",
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
                content: "서버 연결에 실패했습니다. 설정에서 서버 상태를 확인해주세요.",
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

    // 설정 변경 시 재연결
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
}));
