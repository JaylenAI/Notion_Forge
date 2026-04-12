"""Post-processor: AI 생성 블루프린트 검증 + 자동 보정

검증 항목:
1. 필수 블록 존재 여부 (welcome callout, guide toggle)
2. database_ref가 column_list 안에 있는지
3. 빈 spacing paragraph 존재 여부
4. DB 참조 인덱스 유효성
5. 색상 일관성
6. sample_items 최소 개수
7. status 속성값 한국어 매핑
"""

import logging

logger = logging.getLogger("notionforge.post_processor")

from typing import Any


class BlueprintValidator:
    """AI 생성 블루프린트를 검증하고 자동 보정"""

    def validate_and_fix(self, content: dict[str, Any]) -> dict[str, Any]:
        """전체 검증 파이프라인 실행. 보정된 content 반환."""
        content = self._ensure_welcome_callout(content)
        content = self._ensure_guide_toggle(content)
        content = self._fix_db_ref_in_columns(content)
        content = self._ensure_spacing(content)
        content = self._validate_db_refs(content)
        content = self._fix_status_values(content)
        content = self._ensure_sample_items(content)
        content = self._ensure_cover_category(content)
        return content

    def _ensure_welcome_callout(self, content: dict[str, Any]) -> dict[str, Any]:
        """첫 번째 블록이 callout인지 확인, 없으면 추가"""
        blocks = content.get("blocks", [])
        if not blocks:
            return content

        first = blocks[0]
        if first.get("type") != "callout":
            title = content.get("title", "My Template")
            icon = content.get("icon", "📋")
            color = content.get("color", "blue")
            bg = f"{color}_background" if color != "default" else "blue_background"
            welcome = {
                "type": "callout",
                "text": f"{title}에 오신 것을 환영합니다!",
                "icon": icon,
                "color": bg,
            }
            content["blocks"] = [welcome] + blocks
        return content

    def _ensure_guide_toggle(self, content: dict[str, Any]) -> dict[str, Any]:
        """마지막에 사용 가이드 toggle이 있는지 확인"""
        blocks = content.get("blocks", [])
        if not blocks:
            return content

        has_guide = any(
            b.get("type") == "toggle" and "가이드" in b.get("text", "")
            for b in blocks
        )
        if not has_guide:
            blocks.append({
                "type": "toggle",
                "text": "📖 사용 가이드",
                "children_text": "이 템플릿의 사용법을 확인하세요.",
            })
            content["blocks"] = blocks
        return content

    def _fix_db_ref_in_columns(self, content: dict[str, Any]) -> dict[str, Any]:
        """column_list 안의 database_ref를 바깥으로 이동"""
        blocks = content.get("blocks", [])
        fixed_blocks: list[dict] = []
        extracted_refs: list[dict] = []

        for block in blocks:
            if not isinstance(block, dict):
                continue
            if block.get("type") == "column_list":
                columns = block.get("columns", [])
                clean_columns = []
                for col in columns:
                    if isinstance(col, list):
                        clean_col = []
                        for item in col:
                            if item.get("type") == "database_ref":
                                extracted_refs.append(item)
                            else:
                                clean_col.append(item)
                        clean_columns.append(clean_col)
                    else:
                        clean_columns.append(col)
                block["columns"] = clean_columns
                fixed_blocks.append(block)
                # 추출된 DB ref를 column_list 바로 뒤에 배치
                for ref in extracted_refs:
                    fixed_blocks.append({"type": "paragraph", "text": ""})
                    fixed_blocks.append(ref)
                extracted_refs = []
            else:
                fixed_blocks.append(block)

        content["blocks"] = fixed_blocks
        return content

    def _ensure_spacing(self, content: dict[str, Any]) -> dict[str, Any]:
        """주요 섹션 사이에 빈 paragraph 확인"""
        blocks = content.get("blocks", [])
        if len(blocks) < 3:
            return content

        spaced: list[dict] = [blocks[0]]
        section_types = {"heading_1", "heading_2", "database_ref", "divider"}

        for i in range(1, len(blocks)):
            curr = blocks[i]
            if not isinstance(curr, dict):
                continue
            prev = spaced[-1] if spaced else {}

            # 섹션 블록 앞에 spacing이 없으면 추가
            if (
                curr.get("type") in section_types
                and prev.get("type") != "paragraph"
                and prev.get("type") not in section_types
            ):
                # 이미 빈 paragraph가 있으면 스킵
                if not (prev.get("type") == "paragraph" and prev.get("text", "") == ""):
                    spaced.append({"type": "paragraph", "text": ""})

            spaced.append(curr)

        content["blocks"] = spaced
        return content

    def _validate_db_refs(self, content: dict[str, Any]) -> dict[str, Any]:
        """database_ref의 db_index가 유효한 범위인지 확인"""
        db_count = len(content.get("databases", []))
        if db_count == 0:
            return content

        blocks = content.get("blocks", [])
        for block in blocks:
            if not isinstance(block, dict):
                continue
            if block.get("type") == "database_ref":
                idx = block.get("db_index", 0)
                if idx >= db_count:
                    block["db_index"] = 0

            if block.get("type") == "linked_view":
                idx = block.get("db_index", 0)
                if idx >= db_count:
                    block["db_index"] = 0

        content["blocks"] = blocks
        return content

    def _fix_status_values(self, content: dict[str, Any]) -> dict[str, Any]:
        """status 속성의 sample_items 값을 한국어로 매핑"""
        status_map = {
            "not started": "시작 전",
            "in progress": "진행 중",
            "done": "완료",
            "completed": "완료",
            "todo": "시작 전",
            "to do": "시작 전",
        }

        for db in content.get("databases", []):
            props = db.get("db_properties", {})
            status_keys = [k for k, v in props.items() if v == "status" or (isinstance(v, dict) and v.get("type") == "status")]

            for item in db.get("sample_items", []):
                for key in status_keys:
                    val = item.get(key, "")
                    if isinstance(val, str) and val.lower() in status_map:
                        item[key] = status_map[val.lower()]

        return content

    def _ensure_sample_items(self, content: dict[str, Any]) -> dict[str, Any]:
        """각 DB에 최소 3개 sample_items 확인"""
        for db in content.get("databases", []):
            items = db.get("sample_items", [])
            if len(items) < 3:
                # 최소 개수 미달이면 경고만 (자동 생성은 위험)
                logger.info(f"[PostProcessor] 경고: DB '{db.get('title', '?')}' sample_items {len(items)}개 (최소 3개 권장)")
        return content

    def _ensure_cover_category(self, content: dict[str, Any]) -> dict[str, Any]:
        """cover_category가 없으면 color 기반으로 추론"""
        if not content.get("cover_category"):
            color = content.get("color", "blue")
            color_to_category = {
                "blue": "business",
                "green": "nature",
                "orange": "fitness",
                "purple": "creative",
                "pink": "minimal",
                "red": "creative",
                "yellow": "nature",
                "gray": "minimal",
            }
            content["cover_category"] = color_to_category.get(color, "minimal")
        return content


# 싱글턴
blueprint_validator = BlueprintValidator()
