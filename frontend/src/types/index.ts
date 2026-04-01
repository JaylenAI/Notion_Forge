export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  metadata?: {
    type?: string;
    notionUrl?: string;
    blueprint?: Record<string, unknown>;
    progress?: { current: number; total: number };
    step?: string;
  };
}

export interface Settings {
  notionKey: string;
  pageId: string;
  aiKey: string;
  aiModel: string;
}

export interface AiModel {
  id: string;
  name: string;
}

export type ConnectionStatus = "connected" | "disconnected" | "connecting";
