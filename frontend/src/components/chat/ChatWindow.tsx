import { useEffect, useRef } from "react";
import { useChatStore } from "../../stores/chatStore";
import MessageBubble from "./MessageBubble";
import InputBar from "./InputBar";
import ProgressBar from "../common/ProgressBar";

export default function ChatWindow() {
  const { messages, isLoading, connect, currentStep } = useChatStore();
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    connect();
    return () => useChatStore.getState().disconnect();
  }, [connect]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const templates = [
    {
      icon: "📊",
      title: "프로젝트 대시보드",
      desc: "진행 상황, 일정, 팀원 현황을 한눈에",
      prompt: "프로젝트 관리 대시보드 만들어줘, 모던하게",
    },
    {
      icon: "✅",
      title: "습관 트래커",
      desc: "매일 습관을 기록하고 달성률 확인",
      prompt: "습관 트래커 만들어줘, 깔끔하게",
    },
    {
      icon: "📚",
      title: "독서 기록",
      desc: "읽은 책, 메모, 평점을 정리",
      prompt: "독서 기록 노트 만들어줘",
    },
    {
      icon: "🏢",
      title: "온보딩 가이드",
      desc: "신규 입사자를 위한 체크리스트",
      prompt: "신규 입사자 온보딩 가이드 만들어줘",
    },
  ];

  return (
    <div className="flex flex-1 flex-col bg-zinc-800">
      {/* Messages area */}
      <div className="flex-1 overflow-y-auto">
        {messages.length === 0 ? (
          <div className="flex h-full flex-col items-center justify-center px-6">
            <div className="mb-8 text-center">
              <div className="mb-4 inline-flex h-16 w-16 items-center justify-center rounded-2xl bg-indigo-600/20">
                <span className="text-3xl">⚡</span>
              </div>
              <h2 className="mb-2 text-2xl font-semibold text-white">
                NotionForge
              </h2>
              <p className="text-sm text-zinc-400">
                AI가 노션 템플릿을 자동으로 생성해드립니다.
                <br />
                원하는 템플릿을 설명해주세요.
              </p>
            </div>

            {/* Template cards */}
            <div className="grid w-full max-w-2xl grid-cols-2 gap-3">
              {templates.map((t) => (
                <button
                  key={t.title}
                  onClick={() => useChatStore.getState().sendMessage(t.prompt)}
                  className="group flex flex-col gap-1 rounded-xl border border-zinc-700 bg-zinc-800/50 p-4 text-left transition hover:border-indigo-500/50 hover:bg-zinc-750"
                >
                  <div className="flex items-center gap-2">
                    <span className="text-lg">{t.icon}</span>
                    <span className="text-sm font-medium text-white group-hover:text-indigo-300">
                      {t.title}
                    </span>
                  </div>
                  <span className="text-xs text-zinc-500">{t.desc}</span>
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="mx-auto max-w-3xl px-6 py-6">
            {messages.map((msg) => (
              <MessageBubble key={msg.id} message={msg} />
            ))}
            {isLoading && (
              <div className="mb-4 animate-fade-in">
                <ProgressBar step={currentStep} />
              </div>
            )}
            <div ref={bottomRef} />
          </div>
        )}
      </div>

      {/* Input */}
      <InputBar />
    </div>
  );
}
