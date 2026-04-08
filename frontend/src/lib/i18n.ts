type Lang = "ko" | "en" | "ja";

const translations: Record<string, Record<Lang, string>> = {
  // Chat
  "chat.placeholder": {
    ko: "원하는 템플릿을 설명해주세요...",
    en: "Describe the template you want to create...",
    ja: "作りたいテンプレートを説明してください...",
  },
  "chat.connected": {
    ko: "연결 완료! 어떤 템플릿을 만들어드릴까요?",
    en: "Connected! What template would you like to create?",
    ja: "接続完了！どんなテンプレートを作りましょうか？",
  },
  // Library
  "library.title": {
    ko: "템플릿 라이브러리",
    en: "Template Library",
    ja: "テンプレートライブラリ",
  },
  "library.description": {
    ko: "AI가 생성한 노션 템플릿과 커뮤니티 레시피",
    en: "Your templates and community recipes.",
    ja: "AIが生成したNotionテンプレートとコミュニティレシピ",
  },
  "library.myTemplates": {
    ko: "내 템플릿",
    en: "My Templates",
    ja: "マイテンプレート",
  },
  "library.recipes": {
    ko: "커뮤니티 레시피",
    en: "Community Recipes",
    ja: "コミュニティレシピ",
  },
  "library.empty": {
    ko: "아직 저장된 템플릿이 없습니다",
    en: "No templates saved yet",
    ja: "まだテンプレートがありません",
  },
  // Complexity
  "complexity.simple": {
    ko: "간단",
    en: "Simple",
    ja: "シンプル",
  },
  "complexity.standard": {
    ko: "표준",
    en: "Standard",
    ja: "スタンダード",
  },
  "complexity.advanced": {
    ko: "고급",
    en: "Advanced",
    ja: "アドバンスド",
  },
  // Navigation
  "nav.dashboard": { ko: "대시보드", en: "Dashboard", ja: "ダッシュボード" },
  "nav.library": { ko: "라이브러리", en: "Library", ja: "ライブラリ" },
  "nav.integrations": { ko: "연동 설정", en: "Integrations", ja: "連携設定" },
  "nav.profile": { ko: "프로필", en: "Profile", ja: "プロフィール" },
  "nav.support": { ko: "도움말", en: "Support", ja: "サポート" },
  // Actions
  "action.send": { ko: "전송", en: "Send", ja: "送信" },
  "action.cancel": { ko: "취소", en: "Cancel", ja: "キャンセル" },
  "action.save": { ko: "저장", en: "Save", ja: "保存" },
  "action.delete": { ko: "삭제", en: "Delete", ja: "削除" },
  "action.export": { ko: "내보내기", en: "Export", ja: "エクスポート" },
  "action.import": { ko: "가져오기", en: "Import", ja: "インポート" },
  "action.openInNotion": { ko: "노션에서 열기", en: "Open in Notion", ja: "Notionで開く" },
  "action.saveToLibrary": { ko: "라이브러리에 저장", en: "Save to Library", ja: "ライブラリに保存" },
  "action.createAnother": { ko: "새로 만들기", en: "Create Another", ja: "新規作成" },
  "action.useTemplate": { ko: "사용하기", en: "Use Template", ja: "テンプレートを使用" },
};

let currentLang: Lang = "ko";

export function setLang(lang: Lang): void {
  currentLang = lang;
}

export function getLang(): Lang {
  return currentLang;
}

export function t(key: string): string {
  const entry = translations[key];
  if (!entry) return key;
  return entry[currentLang] ?? entry.en ?? key;
}

export default t;
