"""Plan-Execute-Reflect Agent Loop

AI가 도구를 직접 선택하고 실행하는 에이전틱 루프:
1. Plan: 사용자 요청을 분석하고 실행 계획 수립 (Function Calling 또는 프롬프트)
2. Execute: 계획에 따라 도구 실행
3. Reflect: 결과 검증 후 다음 스텝 결정 (최대 1회 재시도)
"""

import json
import logging
from typing import Any, AsyncGenerator

from app.agent.providers.router import ProviderRouter
from app.agent.tools.registry import ToolRegistry
from app.notion.client import NotionClient

logger = logging.getLogger("notionforge.agent_loop")

PLANNER_SYSTEM = """You are a Notion template creation PLANNER.

Given a user request and available tools, output a JSON execution plan.

Available tools:
{tool_descriptions}

Output format:
{{
  "plan": [
    {{"step": 1, "tool": "create_page", "args": {{"parent_id": "...", "title": "..."}}, "description": "메인 페이지 생성"}},
    {{"step": 2, "tool": "create_database", "args": {{"parent_id": "$step1.id", "title": "...", "properties": {{...}}}}, "description": "DB 생성"}},
    ...
  ],
  "reasoning": "왜 이 계획을 선택했는지 1문장"
}}

Rules:
- $stepN.id refers to the result ID from step N
- Always create the main page first
- Create databases before adding items
- Maximum 15 steps per plan
- Use Korean titles and content
"""

REFLECTOR_SYSTEM = """You are a Notion template REFLECTOR.

Given the execution results so far, decide the next action:
1. "continue" - proceed with the next planned step
2. "retry" - retry the failed step with modified args
3. "done" - all steps complete, template is ready

Output JSON:
{{
  "action": "continue|retry|done",
  "feedback": "결과 분석 1문장",
  "modified_args": {{}} // only for retry
}}
"""


class AgentLoop:
    def __init__(self, client: NotionClient, api_key: str = "", ai_model: str = ""):
        self.registry = ToolRegistry(client)
        self.provider = ProviderRouter.resolve(api_key=api_key, ai_model=ai_model)
        self.ai_model = ai_model
        self.step_results: dict[int, dict[str, Any]] = {}

    async def run(self, user_message: str, parent_page_id: str) -> dict[str, Any]:
        plan = await self._plan(user_message, parent_page_id)
        if not plan:
            return {"success": False, "error": "계획 수립 실패"}

        steps = plan.get("plan", [])
        logger.info(f"[AgentLoop] {len(steps)}단계 계획 수립: {plan.get('reasoning', '')}")

        for step in steps:
            step_num = step.get("step", 0)
            tool_name = step.get("tool", "")
            args = self._resolve_refs(step.get("args", {}))
            description = step.get("description", "")

            logger.info(f"[AgentLoop] Step {step_num}: {tool_name} — {description}")

            result = await self.registry.execute(tool_name, **args)

            if "error" in result:
                reflection = await self._reflect(step, result)
                if reflection.get("action") == "retry":
                    modified = {**args, **reflection.get("modified_args", {})}
                    result = await self.registry.execute(tool_name, **modified)

            self.step_results[step_num] = result
            logger.info(f"[AgentLoop] Step {step_num} 완료: id={result.get('id', 'N/A')}")

        main_page_result = self.step_results.get(1, {})
        return {
            "success": True,
            "page_id": main_page_result.get("id"),
            "page_url": main_page_result.get("url"),
            "steps_completed": len(self.step_results),
            "steps_total": len(steps),
        }

    async def run_streaming(self, user_message: str, parent_page_id: str) -> AsyncGenerator[dict[str, Any], None]:
        """스트리밍 버전 — 각 단계별 진행 이벤트를 yield"""
        yield {"type": "progress", "step": "planning", "message": "🧠 실행 계획을 수립하고 있어요..."}

        plan = await self._plan(user_message, parent_page_id)
        if not plan:
            yield {"type": "error", "content": "계획 수립에 실패했습니다."}
            return

        steps = plan.get("plan", [])
        total = len(steps)
        yield {
            "type": "progress",
            "step": "plan_done",
            "message": f"✅ {total}단계 계획 수립 완료: {plan.get('reasoning', '')}",
        }

        for step in steps:
            step_num = step.get("step", 0)
            tool_name = step.get("tool", "")
            args = self._resolve_refs(step.get("args", {}))
            description = step.get("description", "")

            yield {
                "type": "progress",
                "step": "executing",
                "message": f"⚙️ [{step_num}/{total}] {description}",
            }

            result = await self.registry.execute(tool_name, **args)

            if "error" in result:
                yield {
                    "type": "progress",
                    "step": "reflecting",
                    "message": f"🔍 Step {step_num} 오류 분석 중...",
                }
                reflection = await self._reflect(step, result)
                if reflection.get("action") == "retry":
                    modified = {**args, **reflection.get("modified_args", {})}
                    result = await self.registry.execute(tool_name, **modified)

            self.step_results[step_num] = result

        main_page_result = self.step_results.get(1, {})
        yield {
            "type": "result",
            "result": {
                "success": True,
                "page_id": main_page_result.get("id"),
                "page_url": main_page_result.get("url"),
                "steps_completed": len(self.step_results),
                "steps_total": total,
            },
        }

    async def _plan(self, user_message: str, parent_page_id: str) -> dict[str, Any] | None:
        enriched_message = f"Parent page ID: {parent_page_id}\nUser request: {user_message}"

        if self.provider.supports_function_calling:
            tool_specs = self.registry.get_tool_specs()
            system = PLANNER_SYSTEM.format(tool_descriptions=self.registry.get_tool_descriptions())

            max_chars = self.provider.get_max_prompt_chars()
            if max_chars > 0 and len(system) > max_chars:
                system = system[:max_chars]

            result = await self.provider.call_with_tools(system, enriched_message, tool_specs, model=self.ai_model)
            if result and "tool_calls" in result:
                steps = [
                    {
                        "step": i + 1,
                        "tool": tc["name"],
                        "args": tc["arguments"],
                        "description": f"{tc['name']} 실행",
                    }
                    for i, tc in enumerate(result["tool_calls"])
                ]
                return {"plan": steps, "reasoning": "Function Calling 기반 계획"}
            if result:
                return result

        system = PLANNER_SYSTEM.format(tool_descriptions=self.registry.get_tool_descriptions())

        max_chars = self.provider.get_max_prompt_chars()
        if max_chars > 0 and len(system) > max_chars:
            system = system[:max_chars]

        return await self.provider.call(system, enriched_message, model=self.ai_model)

    async def _reflect(self, step: dict, result: dict) -> dict[str, Any]:
        context = json.dumps({"step": step, "result": result}, ensure_ascii=False, default=str)[:2000]
        reflection = await self.provider.call(REFLECTOR_SYSTEM, context, model=self.ai_model)
        return reflection or {"action": "continue"}

    def _resolve_refs(self, args: dict[str, Any]) -> dict[str, Any]:
        resolved = {}
        for key, value in args.items():
            if isinstance(value, str) and value.startswith("$step"):
                try:
                    parts = value.split(".")
                    step_num = int(parts[0].replace("$step", ""))
                    field = parts[1] if len(parts) > 1 else "id"
                    resolved[key] = self.step_results.get(step_num, {}).get(field, value)
                except (ValueError, IndexError):
                    resolved[key] = value
            else:
                resolved[key] = value
        return resolved
