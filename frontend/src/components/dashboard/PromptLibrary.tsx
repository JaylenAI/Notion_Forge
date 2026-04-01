import { useState } from "react";

interface PromptTemplate {
  readonly icon: string;
  readonly title: string;
  readonly prompt: string;
  readonly description: string;
}

interface PromptCategory {
  readonly name: string;
  readonly icon: string;
  readonly color: string;
  readonly templates: readonly PromptTemplate[];
}

const PROMPT_CATEGORIES: readonly PromptCategory[] = [
  {
    name: "Business",
    icon: "business_center",
    color: "text-blue-400 bg-blue-400/10 border-blue-400/20",
    templates: [
      { icon: "\u{1F4CB}", title: "Meeting Notes", prompt: "팀 회의록 템플릿 만들어줘. 참석자, 안건, 결정사항, 액션아이템 포함", description: "회의 관리" },
      { icon: "\u{1F3AF}", title: "OKR Tracker", prompt: "OKR 추적 대시보드 만들어줘. 분기별 목표, 핵심 결과, 진행률 포함", description: "목표 관리" },
      { icon: "\u{1F4CA}", title: "Project Board", prompt: "프로젝트 관리 칸반 보드 만들어줘. 상태별 필터링, 담당자, 마감일 포함", description: "프로젝트 관리" },
      { icon: "\u{1F91D}", title: "CRM", prompt: "고객 관리(CRM) 데이터베이스 만들어줘. 고객 정보, 연락 이력, 딜 파이프라인 포함", description: "고객 관리" },
      { icon: "\u{1F4C5}", title: "Sprint Planning", prompt: "스프린트 플래닝 보드 만들어줘. 스토리 포인트, 백로그, 스프린트 리뷰 포함", description: "애자일 개발" },
    ],
  },
  {
    name: "Personal",
    icon: "person",
    color: "text-green-400 bg-green-400/10 border-green-400/20",
    templates: [
      { icon: "\u{1F4B0}", title: "Budget Manager", prompt: "가계부 만들어줘. 수입/지출 카테고리, 월별 예산, 저축 목표 포함", description: "재무 관리" },
      { icon: "\u{1F3CB}\uFE0F", title: "Workout Tracker", prompt: "운동 기록 일지 만들어줘. 운동 종류, 세트/횟수, 주간 목표 포함", description: "운동 관리" },
      { icon: "\u{1F4DA}", title: "Reading Log", prompt: "독서 기록장 만들어줘. 책 정보, 독서 진행률, 메모, 평점 포함", description: "독서 관리" },
      { icon: "\u{1F9D8}", title: "Habit Tracker", prompt: "습관 추적기 만들어줘. 일일 체크리스트, 연속 달성일, 주간 리포트 포함", description: "습관 관리" },
      { icon: "\u2708\uFE0F", title: "Travel Planner", prompt: "여행 계획표 만들어줘. 일정, 숙소, 예산, 체크리스트 포함", description: "여행 계획" },
    ],
  },
  {
    name: "Content",
    icon: "edit_note",
    color: "text-purple-400 bg-purple-400/10 border-purple-400/20",
    templates: [
      { icon: "\u{1F4DD}", title: "Content Calendar", prompt: "콘텐츠 캘린더 만들어줘. 플랫폼별 일정, 상태, 카테고리 포함", description: "콘텐츠 관리" },
      { icon: "\u{1F4F1}", title: "Social Media Plan", prompt: "SNS 콘텐츠 기획 보드 만들어줘. 채널별 일정, 해시태그, 성과 추적 포함", description: "소셜미디어" },
      { icon: "\u{1F3A5}", title: "Video Production", prompt: "영상 제작 파이프라인 만들어줘. 기획-촬영-편집-배포 단계별 관리 포함", description: "영상 제작" },
      { icon: "\u270D\uFE0F", title: "Blog Posts", prompt: "블로그 포스트 관리 시스템 만들어줘. 아이디어-초안-리뷰-발행 워크플로우 포함", description: "블로그 관리" },
    ],
  },
  {
    name: "Learning",
    icon: "school",
    color: "text-yellow-400 bg-yellow-400/10 border-yellow-400/20",
    templates: [
      { icon: "\u{1F4D6}", title: "Course Tracker", prompt: "온라인 강의 추적기 만들어줘. 강의 목록, 진도율, 노트, 일정 포함", description: "학습 관리" },
      { icon: "\u{1F9E0}", title: "Study Planner", prompt: "학습 계획표 만들어줘. 과목별 일정, 복습 주기, 시험 일정 포함", description: "학습 계획" },
      { icon: "\u{1F4DD}", title: "Research Notes", prompt: "리서치 노트 데이터베이스 만들어줘. 출처, 키워드, 요약, 인사이트 포함", description: "연구 관리" },
      { icon: "\u{1F30D}", title: "Language Learning", prompt: "외국어 학습 트래커 만들어줘. 단어장, 문법 노트, 학습 시간 기록 포함", description: "언어 학습" },
    ],
  },
];

interface PromptLibraryProps {
  readonly open: boolean;
  readonly onClose: () => void;
  readonly onSelect: (prompt: string) => void;
}

function PromptLibrary({ open, onClose, onSelect }: PromptLibraryProps) {
  const [activeCategory, setActiveCategory] = useState(0);

  if (!open) return null;

  const category = PROMPT_CATEGORIES[activeCategory];

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4" onClick={onClose}>
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" />
      <div
        className="relative w-full max-w-2xl max-h-[70vh] bg-[var(--surface-container,#201f1f)] border border-[var(--border-color,#424656)] rounded-2xl shadow-2xl overflow-hidden animate-fade-in flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-[var(--border-color,#424656)]/30">
          <div>
            <h2 className="text-lg font-bold font-headline text-[var(--text-primary,#e5e2e1)]">Prompt Library</h2>
            <p className="text-xs text-[var(--text-muted,#c2c6d8)]/50 mt-0.5">Choose a template to get started quickly</p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="w-8 h-8 rounded-lg flex items-center justify-center text-[var(--text-muted,#c2c6d8)]/50 hover:text-[var(--text-primary,#e5e2e1)] hover:bg-[var(--surface-container-high,#2a2a2a)] transition-colors"
          >
            <span className="material-symbols-outlined text-lg">close</span>
          </button>
        </div>

        {/* Category tabs */}
        <div className="flex gap-2 px-6 py-3 border-b border-[var(--border-color,#424656)]/20 overflow-x-auto">
          {PROMPT_CATEGORIES.map((cat, i) => (
            <button
              key={cat.name}
              type="button"
              onClick={() => setActiveCategory(i)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-colors border ${
                i === activeCategory
                  ? cat.color
                  : "text-[var(--text-muted,#c2c6d8)]/50 border-transparent hover:bg-[var(--surface-container-high,#2a2a2a)]"
              }`}
            >
              <span className="material-symbols-outlined text-sm">{cat.icon}</span>
              {cat.name}
            </button>
          ))}
        </div>

        {/* Template grid */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {category?.templates.map((tpl) => (
              <button
                key={tpl.title}
                type="button"
                onClick={() => { onSelect(tpl.prompt); onClose(); }}
                className="flex items-start gap-3 p-4 rounded-xl border border-[var(--border-color,#424656)]/20 bg-[var(--surface-container-high,#2a2a2a)]/50 hover:bg-[var(--surface-container-high,#2a2a2a)] hover:border-[#adc6ff]/30 transition-all text-left group"
              >
                <span className="text-2xl">{tpl.icon}</span>
                <div className="min-w-0">
                  <p className="text-sm font-medium text-[var(--text-primary,#e5e2e1)] group-hover:text-[#adc6ff] transition-colors">{tpl.title}</p>
                  <p className="text-[11px] text-[var(--text-muted,#c2c6d8)]/50 mt-0.5">{tpl.description}</p>
                  <p className="text-[10px] text-[var(--text-muted,#c2c6d8)]/30 mt-1 truncate">{tpl.prompt}</p>
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default PromptLibrary;
