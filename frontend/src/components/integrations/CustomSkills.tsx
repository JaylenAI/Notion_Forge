import { useState, useEffect, useCallback } from "react";
import toast from "react-hot-toast";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:9500";

interface Skill {
  readonly id: string;
  readonly name: string;
  readonly description: string;
  readonly is_custom: boolean;
  readonly keywords: string;
}

const SKILL_TEMPLATE = `이 스킬은 [목적]을 위한 노션 템플릿을 만듭니다.

## Template Structure

### Layout
Single column (clean)

### Block Order
1. callout: 환영 메시지 (테마 색상)
2. divider
3. heading_1: 메인 섹션
4. database_ref: 인라인 데이터베이스
5. divider
6. toggle: 사용 가이드

## Database Properties
- 이름: title
- 상태: status
- 날짜: date
- 메모: rich_text

## Views
- table (기본)
- board (상태별)

## Sample Data
5개 이상의 현실적인 한국어 샘플 데이터 포함`;

function CustomSkills() {
  const [skills, setSkills] = useState<Skill[]>([]);
  const [loading, setLoading] = useState(true);
  const [showEditor, setShowEditor] = useState(false);
  const [editingSkill, setEditingSkill] = useState<string | null>(null);

  // Form state
  const [formId, setFormId] = useState("");
  const [formName, setFormName] = useState("");
  const [formDesc, setFormDesc] = useState("");
  const [formKeywords, setFormKeywords] = useState("");
  const [formContent, setFormContent] = useState(SKILL_TEMPLATE);

  const fetchSkills = useCallback(async () => {
    try {
      const resp = await fetch(`${API_URL}/api/skills`);
      const data = await resp.json();
      setSkills(data.skills ?? []);
    } catch {
      setSkills([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSkills();
  }, [fetchSkills]);

  const handleNew = () => {
    setEditingSkill(null);
    setFormId("");
    setFormName("");
    setFormDesc("");
    setFormKeywords("");
    setFormContent(SKILL_TEMPLATE);
    setShowEditor(true);
  };

  const handleEdit = async (skillId: string) => {
    try {
      const resp = await fetch(`${API_URL}/api/skills/${skillId}`);
      const data = await resp.json();
      if (data.content) {
        setEditingSkill(skillId);
        setFormId(skillId);
        // Parse frontmatter
        const lines = data.content.split("\n");
        let inFrontmatter = false;
        let bodyStart = 0;
        for (let i = 0; i < lines.length; i++) {
          if (lines[i].trim() === "---") {
            if (inFrontmatter) { bodyStart = i + 1; break; }
            inFrontmatter = true;
          } else if (inFrontmatter) {
            if (lines[i].startsWith("name:")) setFormName(lines[i].split(":").slice(1).join(":").trim());
            if (lines[i].startsWith("description:")) setFormDesc(lines[i].split(":").slice(1).join(":").trim());
            if (lines[i].startsWith("keywords:")) setFormKeywords(lines[i].split(":").slice(1).join(":").trim());
          }
        }
        setFormContent(lines.slice(bodyStart).join("\n").trim());
        setShowEditor(true);
      }
    } catch {
      toast.error("Failed to load skill");
    }
  };

  const handleSave = async () => {
    if (!formId.trim()) { toast.error("Skill ID is required"); return; }
    if (!formName.trim()) { toast.error("Name is required"); return; }

    const method = editingSkill ? "PUT" : "POST";
    const url = editingSkill ? `${API_URL}/api/skills/${editingSkill}` : `${API_URL}/api/skills`;

    try {
      const resp = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          skill_id: formId.trim().toLowerCase().replace(/\s+/g, "_"),
          name: formName.trim(),
          description: formDesc.trim(),
          keywords: formKeywords.trim(),
          content: formContent.trim(),
        }),
      });
      const data = await resp.json();
      if (data.success) {
        toast.success(data.message);
        setShowEditor(false);
        fetchSkills();
      } else {
        toast.error("Save failed");
      }
    } catch {
      toast.error("Save failed");
    }
  };

  const handleDelete = async (skillId: string) => {
    if (!confirm(`Delete custom skill "${skillId}"?`)) return;
    try {
      const resp = await fetch(`${API_URL}/api/skills/${skillId}`, { method: "DELETE" });
      const data = await resp.json();
      if (data.success) {
        toast.success(data.message);
        fetchSkills();
      }
    } catch {
      toast.error("Delete failed");
    }
  };

  if (showEditor) {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-bold text-[var(--text-primary,#e5e2e1)]">
            {editingSkill ? `Edit: ${editingSkill}` : "New Custom Skill"}
          </h3>
          <button
            type="button"
            onClick={() => setShowEditor(false)}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="text-xs text-gray-400 block mb-1">Skill ID (영문, 밑줄)</label>
            <input
              value={formId}
              onChange={(e) => setFormId(e.target.value)}
              disabled={!!editingSkill}
              placeholder="meeting_notes"
              className="w-full bg-[var(--surface-variant,#353534)] border-none rounded-lg text-sm text-[var(--text-primary,#e5e2e1)] px-3 py-2 outline-none focus:ring-1 focus:ring-[#adc6ff] disabled:opacity-50"
            />
          </div>
          <div>
            <label className="text-xs text-gray-400 block mb-1">Name</label>
            <input
              value={formName}
              onChange={(e) => setFormName(e.target.value)}
              placeholder="Meeting Notes"
              className="w-full bg-[var(--surface-variant,#353534)] border-none rounded-lg text-sm text-[var(--text-primary,#e5e2e1)] px-3 py-2 outline-none focus:ring-1 focus:ring-[#adc6ff]"
            />
          </div>
        </div>

        <div>
          <label className="text-xs text-gray-400 block mb-1">Description (AI가 스킬 선택 시 참고)</label>
          <input
            value={formDesc}
            onChange={(e) => setFormDesc(e.target.value)}
            placeholder="회의록 자동 생성 — 안건, 결정사항, 액션아이템 포함"
            className="w-full bg-[var(--surface-variant,#353534)] border-none rounded-lg text-sm text-[var(--text-primary,#e5e2e1)] px-3 py-2 outline-none focus:ring-1 focus:ring-[#adc6ff]"
          />
        </div>

        <div>
          <label className="text-xs text-gray-400 block mb-1">Keywords (쉼표 구분 — AI 매칭용)</label>
          <input
            value={formKeywords}
            onChange={(e) => setFormKeywords(e.target.value)}
            placeholder="회의,미팅,회의록,안건,meeting,minutes"
            className="w-full bg-[var(--surface-variant,#353534)] border-none rounded-lg text-sm text-[var(--text-primary,#e5e2e1)] px-3 py-2 outline-none focus:ring-1 focus:ring-[#adc6ff]"
          />
        </div>

        <div>
          <label className="text-xs text-gray-400 block mb-1">
            Skill Guide (AI 시스템 프롬프트 — 템플릿 구조/속성/규칙 정의)
          </label>
          <textarea
            value={formContent}
            onChange={(e) => setFormContent(e.target.value)}
            rows={16}
            className="w-full bg-[var(--surface-variant,#353534)] border-none rounded-lg text-xs text-[var(--text-primary,#e5e2e1)] px-3 py-2 outline-none focus:ring-1 focus:ring-[#adc6ff] font-mono resize-y"
          />
        </div>

        <div className="flex gap-2 justify-end">
          <button
            type="button"
            onClick={() => setShowEditor(false)}
            className="px-4 py-2 rounded-lg text-sm text-gray-400 hover:text-white transition-colors"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={handleSave}
            className="px-4 py-2 rounded-lg bg-[#adc6ff] text-[#002e69] text-sm font-medium hover:bg-[#bdd3ff] transition-colors"
          >
            {editingSkill ? "Update Skill" : "Create Skill"}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-bold text-[var(--text-primary,#e5e2e1)]">Custom Skills</h3>
          <p className="text-xs text-gray-400 mt-0.5">
            나만의 스킬을 추가하면 AI가 맞춤형 템플릿을 생성합니다
          </p>
        </div>
        <button
          type="button"
          onClick={handleNew}
          className="px-3 py-1.5 rounded-lg bg-[#adc6ff]/10 text-[#adc6ff] text-xs hover:bg-[#adc6ff]/20 transition-colors flex items-center gap-1"
        >
          <span className="material-symbols-outlined text-sm">add</span>
          New Skill
        </button>
      </div>

      {loading ? (
        <div className="text-gray-500 text-center py-8">Loading skills...</div>
      ) : (
        <div className="space-y-2">
          {skills.map((skill) => (
            <div
              key={skill.id}
              className={`flex items-center justify-between p-3 rounded-xl border transition-colors ${
                skill.is_custom
                  ? "bg-[#adc6ff]/5 border-[#adc6ff]/20"
                  : "bg-[var(--surface-variant,#1e1e1e)] border-[var(--border-color,#333)]"
              }`}
            >
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-mono text-[var(--text-primary,#e5e2e1)]">{skill.id}</span>
                  {skill.is_custom && (
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-[#adc6ff]/20 text-[#adc6ff]">custom</span>
                  )}
                </div>
                <p className="text-xs text-gray-400 mt-0.5 truncate">{skill.description}</p>
              </div>
              <div className="flex items-center gap-1 ml-3 shrink-0">
                {skill.is_custom && (
                  <>
                    <button
                      type="button"
                      onClick={() => handleEdit(skill.id)}
                      className="w-8 h-8 rounded-lg flex items-center justify-center text-gray-400 hover:text-white hover:bg-[#2a2a2a] transition-colors"
                      title="Edit"
                    >
                      <span className="material-symbols-outlined text-sm">edit</span>
                    </button>
                    <button
                      type="button"
                      onClick={() => handleDelete(skill.id)}
                      className="w-8 h-8 rounded-lg flex items-center justify-center text-gray-400 hover:text-red-400 hover:bg-red-400/10 transition-colors"
                      title="Delete"
                    >
                      <span className="material-symbols-outlined text-sm">delete</span>
                    </button>
                  </>
                )}
                {!skill.is_custom && (
                  <span className="text-[10px] text-gray-500">built-in</span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default CustomSkills;
