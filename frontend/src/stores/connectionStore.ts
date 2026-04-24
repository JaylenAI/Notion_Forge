import { create } from "zustand";
import type { Message, ConnectionStatus } from "../types";
import { useChatStore } from "./chatStore";
import { useSettingsStore } from "./settingsStore";

export const WS_URL = import.meta.env.VITE_WS_URL ?? "ws://localhost:9500";
export const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:9500";

function ensureString(value: unknown): string {
  if (typeof value === "string") return value;
  if (value == null) return "";
  return JSON.stringify(value);
}

const MAX_RETRIES = 5;
const MAX_BACKOFF_MS = 30_000;

interface ConnectionState {
  connectionStatus: ConnectionStatus;
  ws: WebSocket | null;
  retryCount: number;
  retryTimer: ReturnType<typeof setTimeout> | null;
  connect: () => void;
  disconnect: () => void;
}

function getBackoffMs(retryCount: number): number {
  const ms = Math.min(1000 * Math.pow(2, retryCount), MAX_BACKOFF_MS);
  return ms;
}

export const useConnectionStore = create<ConnectionState>((set, get) => ({
  connectionStatus: "disconnected",
  ws: null,
  retryCount: 0,
  retryTimer: null,

  connect: () => {
    const { ws: existing, connectionStatus } = get();
    if (existing && (existing.readyState === WebSocket.OPEN || existing.readyState === WebSocket.CONNECTING)) return;
    if (connectionStatus === "connecting") return;

    set({ connectionStatus: "connecting" });

    try {
      const ws = new WebSocket(`${WS_URL}/ws/chat`);

      ws.onopen = () => {
        const settings = useSettingsStore.getState().settings;
        set({ connectionStatus: "connected", ws, retryCount: 0 });
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

          const chatSet = useChatStore.setState;

          // progress 이벤트: 실시간 로그 스트림 (messages에는 안 추가)
          if (eventType === "progress") {
            const logMsg = data.message ?? data.step ?? "";
            chatSet((state) => ({
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
              content: ensureString(data.content ?? data.message),
              timestamp: new Date(),
              metadata: { type: "system" },
            };
            chatSet((state) => ({
              messages: [...state.messages, msg],
              isLoading: false,
            }));
            return;
          }

          // approval_request: Approval Gate 대기
          if (eventType === "approval_request") {
            const msg: Message = {
              id: crypto.randomUUID(),
              role: "assistant",
              content: ensureString(data.content) || "템플릿 설계를 확인해주세요. 생성을 진행할까요?",
              timestamp: new Date(),
              metadata: { type: "approval_request", blueprint: data.blueprint },
            };
            chatSet((state) => ({
              messages: [...state.messages, msg],
              pendingApproval: true,
              isLoading: false,
              currentStep: "",
            }));
            return;
          }

          // complete, error, blueprint_preview 등: 메시지에 추가
          const msg: Message = {
            id: crypto.randomUUID(),
            role: "assistant",
            content: ensureString(data.content ?? data.message),
            timestamp: new Date(),
            metadata: {
              type: eventType,
              notionUrl: data.result?.main_url,
              blueprint: data.blueprint,
              step: data.step,
            },
          };

          chatSet((state) => ({
            messages: [...state.messages, msg],
            isLoading: false,
            currentStep: "",
            progressLog: eventType === "complete" || eventType === "error" ? [] : state.progressLog,
          }));
        } catch {
          // ignore parse errors
        }
      };

      ws.onclose = () => {
        set({ connectionStatus: "disconnected", ws: null });

        // Exponential backoff reconnection
        const { retryCount } = get();
        if (retryCount < MAX_RETRIES) {
          const backoff = getBackoffMs(retryCount);
          const timer = setTimeout(() => {
            set({ retryTimer: null });
            get().connect();
          }, backoff);
          set({ retryCount: retryCount + 1, retryTimer: timer });
        }
      };

      ws.onerror = () => {
        set({ connectionStatus: "disconnected" });
      };
    } catch {
      set({ connectionStatus: "disconnected" });
    }
  },

  disconnect: () => {
    const { ws, retryTimer } = get();
    if (retryTimer) {
      clearTimeout(retryTimer);
    }
    ws?.close();
    set({ ws: null, connectionStatus: "disconnected", retryCount: 0, retryTimer: null });
  },
}));
