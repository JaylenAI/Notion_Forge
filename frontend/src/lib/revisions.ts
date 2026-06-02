// 블루프린트 버전 히스토리 (Phase 4/B2) — 세션 메시지에서 blueprint 리비전을 추출.
// 각 생성/수정으로 도착한 blueprint = 하나의 버전. 프리뷰에서 이전 버전 열람/복원에 사용.

export interface Revision {
  readonly blueprint: Record<string, unknown>;
  readonly label: string;
  readonly index: number;
}

interface MessageLike {
  readonly metadata?: { readonly blueprint?: Record<string, unknown> };
}

export function extractRevisions(messages: ReadonlyArray<MessageLike>): Revision[] {
  const revisions: Revision[] = [];
  for (const m of messages) {
    const bp = m.metadata?.blueprint;
    if (bp && typeof bp === "object") {
      const meta = (bp as { metadata?: { title?: string } }).metadata;
      const title = meta?.title?.trim();
      revisions.push({
        blueprint: bp,
        label: title && title.length > 0 ? title : `버전 ${revisions.length + 1}`,
        index: revisions.length,
      });
    }
  }
  return revisions;
}
