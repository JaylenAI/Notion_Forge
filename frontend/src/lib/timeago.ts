const UNITS: readonly [string, number][] = [
  ["년", 31536000],
  ["개월", 2592000],
  ["주", 604800],
  ["일", 86400],
  ["시간", 3600],
  ["분", 60],
  ["초", 1],
];

export function timeAgo(date: Date | string): string {
  const d = typeof date === "string" ? new Date(date) : date;
  const diff = Math.floor((Date.now() - d.getTime()) / 1000);

  if (diff < 5) return "방금 전";

  for (const [label, seconds] of UNITS) {
    const count = Math.floor(diff / seconds);
    if (count >= 1) return `${count}${label} 전`;
  }

  return "방금 전";
}
