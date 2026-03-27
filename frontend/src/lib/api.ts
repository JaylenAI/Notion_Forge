const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:9500";
const WS_URL = import.meta.env.VITE_WS_URL ?? "ws://localhost:9500";

export async function fetchApi<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    throw new Error(`API Error: ${response.status}`);
  }
  return response.json();
}

export function createWebSocket(path: string): WebSocket {
  return new WebSocket(`${WS_URL}${path}`);
}
