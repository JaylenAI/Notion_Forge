"""Post-processor: AI 생성 블루프린트 검증 + 자동 보정 + 디자인 보강

검증 항목:
1. 필수 블록 존재 여부 (welcome callout, guide toggle)
2. database_ref가 column_list 안에 있는지
3. 빈 spacing paragraph 존재 여부
4. DB 참조 인덱스 유효성
5. 색상 일관성
6. sample_items 최소 개수 (부족 시 자동 생성)
7. status 속성값 한국어 매핑
8. 디자인 다양성 보강 (블록 nesting, quote, divider)
"""

import logging
import random
from datetime import datetime, timedelta

logger = logging.getLogger("notionforge.post_processor")

from typing import Any


class BlueprintValidator:
    """AI 생성 블루프린트를 검증하고 자동 보정"""

    def validate_and_fix(self, content: dict[str, Any]) -> dict[str, Any]:
        """전체 검증 파이프라인 실행. 보정된 content 반환."""
        content = self._normalize_fields(content)
        content = self._ensure_welcome_callout(content)
        content = self._ensure_guide_toggle(content)
        content = self._fix_db_ref_in_columns(content)
        content = self._ensure_spacing(content)
        content = self._validate_db_refs(content)
        content = self._fix_status_values(content)
        content = self._ensure_sample_items(content)
        content = self._ensure_sample_icons(content)
        content = self._ensure_cover_category(content)
        content = self._ensure_sub_page_icons(content)
        content = self._label_table_of_contents(content)
        content = self._validate_view_properties(content)
        content = self._enhance_design_diversity(content)
        return content

    def _normalize_fields(self, content: dict[str, Any]) -> dict[str, Any]:
        """AI 응답의 필드 타입을 정규화 (list→str 등)"""
        title = content.get("title", "")
        if isinstance(title, list):
            content["title"] = " ".join(str(t) for t in title) if title else "My Template"
        elif not title:
            content["title"] = "My Template"

        for block in content.get("blocks", []):
            if isinstance(block, dict):
                text = block.get("text")
                if isinstance(text, list):
                    block["text"] = " ".join(str(t) for t in text) if text else ""

        for sub in content.get("sub_pages", []):
            if isinstance(sub, dict):
                for key in ("title", "name"):
                    val = sub.get(key)
                    if isinstance(val, list):
                        sub[key] = " ".join(str(v) for v in val) if val else ""

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

        has_guide = any(b.get("type") == "toggle" and "가이드" in b.get("text", "") for b in blocks)
        if not has_guide:
            blocks.append(
                {
                    "type": "toggle",
                    "text": "📖 사용 가이드",
                    "children_text": "이 템플릿의 사용법을 확인하세요.",
                }
            )
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
        """status 속성의 sample_items 값을 표준 한국어로 통일"""
        status_map = {
            "not started": "시작 전",
            "todo": "시작 전",
            "to do": "시작 전",
            "in progress": "진행 중",
            "doing": "진행 중",
            "done": "완료",
            "completed": "완료",
            "finished": "완료",
            "시작전": "시작 전",
            "대기": "시작 전",
            "미시작": "시작 전",
            "진행중": "진행 중",
            "작업중": "진행 중",
            "완료됨": "완료",
            "끝": "완료",
        }

        for db in content.get("databases", []):
            props = db.get("db_properties", db.get("properties", {}))
            status_keys = [
                k for k, v in props.items() if v == "status" or (isinstance(v, dict) and v.get("type") == "status")
            ]

            for item in db.get("sample_items", []):
                for key in status_keys:
                    val = item.get(key, "")
                    if isinstance(val, str):
                        mapped = status_map.get(val.lower().strip()) or status_map.get(val.strip())
                        if mapped:
                            item[key] = mapped

        return content

    def _ensure_sample_items(self, content: dict[str, Any]) -> dict[str, Any]:
        """각 DB에 최소 3개 sample_items 보장 — 부족하면 속성 기반 자동 생성"""
        for db in content.get("databases", []):
            items = db.get("sample_items", [])
            if len(items) >= 3:
                continue

            props = db.get("db_properties", db.get("properties", {}))
            db_title = db.get("title", "항목")
            needed = 4 - len(items)
            logger.info(f"[PostProcessor] DB '{db_title}' sample_items {len(items)}개 → {needed}개 자동 생성")

            generated = _generate_sample_items(props, db_title, needed, existing=items)
            items.extend(generated)
            db["sample_items"] = items
        return content

    def _ensure_sample_icons(self, content: dict[str, Any]) -> dict[str, Any]:
        """샘플 데이터에 icon이 없으면 자동 부여"""
        icon_pool = ["📌", "📋", "🎯", "📊", "💡", "🔖", "📝", "⭐", "🏷️", "📎"]
        for db in content.get("databases", []):
            for i, item in enumerate(db.get("sample_items", [])):
                if not item.get("icon"):
                    item["icon"] = icon_pool[i % len(icon_pool)]
        return content

    def _label_table_of_contents(self, content: dict[str, Any]) -> dict[str, Any]:
        """table_of_contents 블록 앞에 '📑 목차' heading이 없으면 추가"""
        blocks = content.get("blocks", [])
        i = 0
        while i < len(blocks):
            block = blocks[i]
            if not isinstance(block, dict) or block.get("type") != "table_of_contents":
                i += 1
                continue
            has_label = False
            if i > 0:
                prev = blocks[i - 1]
                if isinstance(prev, dict) and prev.get("type") in ("heading_1", "heading_2", "heading_3"):
                    prev_text = prev.get("text", "")
                    if "목차" in prev_text or "contents" in prev_text.lower():
                        has_label = True
            if not has_label:
                color = content.get("color", "blue")
                label = {"type": "heading_2", "text": "📑 목차", "color": color}
                blocks.insert(i, label)
                i += 1
            i += 1
        content["blocks"] = blocks
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

    def _ensure_sub_page_icons(self, content: dict[str, Any]) -> dict[str, Any]:
        """서브페이지에 아이콘이 없으면 제목 기반으로 추론"""
        icon_hints: dict[str, str] = {
            "공지": "📢",
            "가이드": "📖",
            "FAQ": "❓",
            "설정": "⚙️",
            "자료": "📚",
            "일정": "📅",
            "회의": "🤝",
            "보고": "📊",
            "규칙": "📜",
            "도서": "📚",
            "과제": "📝",
            "게시": "💬",
            "소개": "👋",
            "체크": "✅",
            "목표": "🎯",
            "리소스": "🔗",
            "정책": "📋",
            "프로세스": "🔄",
            "팀": "👥",
            "멤버": "👤",
        }
        for sub in content.get("sub_pages", []):
            if sub.get("icon"):
                continue
            title = sub.get("name", sub.get("title", ""))
            matched_icon = "📄"
            for keyword, icon in icon_hints.items():
                if keyword in title:
                    matched_icon = icon
                    break
            sub["icon"] = matched_icon
        return content

    def _validate_view_properties(self, content: dict[str, Any]) -> dict[str, Any]:
        """뷰 설정의 속성 참조가 실제 DB 속성과 매칭되는지 검증 + 자동 보정"""
        for db in content.get("databases", []):
            props = db.get("db_properties", db.get("properties", {}))
            prop_names = set(props.keys()) if isinstance(props, dict) else set()
            prop_types = {}
            for k, v in props.items() if isinstance(props, dict) else []:
                ptype = v if isinstance(v, str) else v.get("type", "") if isinstance(v, dict) else ""
                prop_types[k] = ptype

            status_props = [k for k, t in prop_types.items() if t == "status"]
            select_props = [k for k, t in prop_types.items() if t in ("status", "select")]
            date_props = [k for k, t in prop_types.items() if t == "date"]

            for view in db.get("views", []):
                if isinstance(view, str):
                    continue
                vtype = view.get("type", view.get("view_type", "table"))

                if vtype == "board":
                    group_by = view.get("group_by")
                    if isinstance(group_by, dict):
                        group_by = group_by.get("property", group_by.get("name", ""))
                        view["group_by"] = group_by
                    if group_by and isinstance(group_by, str) and group_by not in prop_names:
                        fallback = status_props[0] if status_props else (select_props[0] if select_props else None)
                        view["group_by"] = fallback
                        if view["group_by"]:
                            logger.info(f"[ViewFix] board group_by '{group_by}' → '{view['group_by']}'")
                    if not view.get("group_by") and status_props:
                        view["group_by"] = status_props[0]

                elif vtype in ("calendar", "timeline"):
                    date_prop = view.get("date_property") or view.get("date_property_id")
                    if isinstance(date_prop, dict):
                        date_prop = date_prop.get("property", date_prop.get("name", ""))
                        view["date_property"] = date_prop
                    if date_prop and isinstance(date_prop, str) and date_prop not in prop_names:
                        view["date_property"] = date_props[0] if date_props else None
                        if view["date_property"]:
                            logger.info(f"[ViewFix] {vtype} date_property '{date_prop}' → '{view['date_property']}'")
                    if not (view.get("date_property") or view.get("date_property_id")) and date_props:
                        view["date_property"] = date_props[0]

                elif vtype == "chart":
                    x_axis = view.get("x_axis")
                    if x_axis and x_axis not in prop_names:
                        view["x_axis"] = select_props[0] if select_props else None

        return content

    def _enhance_design_diversity(self, content: dict[str, Any]) -> dict[str, Any]:
        """디자인 다양성 보강 — 단조로운 블록 구조에 프리미엄 시각 요소 추가"""
        blocks = content.get("blocks", [])
        if len(blocks) < 3:
            return content

        color = content.get("color", "blue")
        bg = f"{color}_background" if color != "default" else "blue_background"
        block_types = {b.get("type") for b in blocks if isinstance(b, dict)}

        has_quote = "quote" in block_types
        has_divider = "divider" in block_types
        has_column_list = "column_list" in block_types

        # 1. 통계 대시보드 카드 (column_list 없으면 추가)
        databases = content.get("databases", [])
        if not has_column_list and len(databases) >= 2:
            stat_cards = self._build_stat_cards(databases, color)
            if stat_cards:
                insert_pos = next(
                    (i for i, b in enumerate(blocks) if b.get("type") in ("heading_1", "heading_2", "database_ref")),
                    2,
                )
                blocks.insert(insert_pos, stat_cards)

        # 2. 명언/인사이트 인용구
        if not has_quote and len(blocks) >= 5:
            title = content.get("title", "")
            quote_texts = [
                f"'{title}'로 더 체계적인 관리를 시작하세요.",
                "작은 기록이 큰 변화를 만듭니다.",
                "체계적인 관리가 성공의 첫걸음입니다.",
            ]
            quote_block = {
                "type": "quote",
                "text": random.choice(quote_texts),
                "color": bg,
            }
            insert_pos = min(2, len(blocks))
            blocks.insert(insert_pos, quote_block)

        # 3. 섹션 디바이더 (DB ref 앞에 divider 추가)
        if not has_divider and len(blocks) >= 6:
            db_ref_positions = [
                i for i, b in enumerate(blocks) if isinstance(b, dict) and b.get("type") == "database_ref"
            ]
            for offset, pos in enumerate(db_ref_positions):
                actual_pos = pos + offset
                if actual_pos > 0 and blocks[actual_pos - 1].get("type") != "divider":
                    blocks.insert(actual_pos, {"type": "divider"})

        # 4. 섹션 헤딩에 배경색 통일
        section_colors = [bg, f"{color}_background"] if color != "default" else ["blue_background"]
        for b in blocks:
            if isinstance(b, dict) and b.get("type") in ("heading_1", "heading_2"):
                if not b.get("color"):
                    b["color"] = section_colors[0]

        # 5. 중첩 콘텐츠 (callout에 children 추가)
        children_count = sum(1 for b in blocks if isinstance(b, dict) and (b.get("children") or b.get("children_text")))
        if children_count < 2:
            for b in blocks:
                if not isinstance(b, dict):
                    continue
                if b.get("type") == "callout" and not b.get("children"):
                    text = b.get("text", "")
                    if len(text) > 10:
                        b["children"] = [
                            {"type": "paragraph", "text": "아래 내용을 참고하여 활용해보세요."},
                        ]
                        children_count += 1
                        if children_count >= 2:
                            break

        content["blocks"] = blocks
        return content

    @staticmethod
    def _build_stat_cards(databases: list[dict[str, Any]], color: str) -> dict[str, Any] | None:
        """DB 기반 통계 요약 카드 (column_list) 자동 생성"""
        color_map = {
            "blue": ["blue_background", "green_background", "purple_background"],
            "green": ["green_background", "blue_background", "orange_background"],
            "orange": ["orange_background", "blue_background", "green_background"],
            "purple": ["purple_background", "blue_background", "pink_background"],
            "red": ["red_background", "orange_background", "blue_background"],
            "pink": ["pink_background", "purple_background", "blue_background"],
        }
        colors = color_map.get(color, ["blue_background", "green_background", "purple_background"])

        stat_icons = ["📊", "📋", "🎯", "💡", "📈", "✅"]
        columns = []

        for i, db in enumerate(databases[:3]):
            title = db.get("title", f"DB {i + 1}")
            sample_count = len(db.get("sample_items", []))
            icon = stat_icons[i % len(stat_icons)]
            bg_color = colors[i % len(colors)]
            columns.append(
                [
                    {
                        "type": "callout",
                        "text": f"{icon} {title}\n{sample_count}건",
                        "icon": icon,
                        "color": bg_color,
                    }
                ]
            )

        if len(columns) < 2:
            return None

        return {"type": "column_list", "columns": columns}


def _generate_sample_items(
    props: dict[str, Any],
    db_title: str,
    count: int,
    existing: list[dict] | None = None,
) -> list[dict[str, Any]]:
    """속성 타입 기반으로 현실적인 샘플 데이터 자동 생성"""
    existing = existing or []
    existing_titles: set[str] = set()
    for item in existing:
        for v in item.values():
            if isinstance(v, str):
                existing_titles.add(v)
                break

    title_key = ""
    for k, v in props.items():
        ptype = v if isinstance(v, str) else v.get("type", "") if isinstance(v, dict) else ""
        if ptype == "title":
            title_key = k
            break
    if not title_key:
        title_key = "이름"

    title_pools: dict[str, list[str]] = {
        "default": ["프로젝트 A", "프로젝트 B", "프로젝트 C", "프로젝트 D", "프로젝트 E"],
    }
    title_hints = db_title.lower()
    if any(w in title_hints for w in ["자료", "학습", "교재", "수업", "강의"]):
        title_pools["matched"] = ["파이썬 기초", "데이터 분석 입문", "프로젝트 관리론", "UX 디자인 원리", "마케팅 전략"]
    elif any(w in title_hints for w in ["일정", "캘린더", "스케줄"]):
        title_pools["matched"] = ["팀 미팅", "프로젝트 리뷰", "1:1 면담", "워크숍", "마감일"]
    elif any(w in title_hints for w in ["과제", "태스크", "할일"]):
        title_pools["matched"] = ["보고서 작성", "자료 조사", "발표 준비", "코드 리뷰", "문서 정리"]
    elif any(w in title_hints for w in ["멤버", "팀원", "학생", "인원"]):
        title_pools["matched"] = ["김민수", "이서연", "박준혁", "정하윤", "최도윤"]
    elif any(w in title_hints for w in ["예산", "비용", "지출", "가계"]):
        title_pools["matched"] = ["사무용품 구매", "팀 회식", "출장 교통비", "소프트웨어 구독", "교육 수강료"]
    elif any(w in title_hints for w in ["회의", "미팅"]):
        title_pools["matched"] = ["주간 스탠드업", "분기 리뷰", "브레인스토밍", "클라이언트 미팅", "팀 회고"]
    elif any(w in title_hints for w in ["운동", "피트니스", "헬스"]):
        title_pools["matched"] = ["아침 러닝 5km", "스쿼트 4세트", "플랭크 3분", "수영 30분", "요가 스트레칭"]
    elif any(w in title_hints for w in ["독서", "책", "도서"]):
        title_pools["matched"] = ["원씽", "아주 작은 습관의 힘", "사피엔스", "부의 추월차선", "심리학의 즐거움"]
    elif any(w in title_hints for w in ["영화", "시청", "드라마"]):
        title_pools["matched"] = ["인터스텔라", "기생충", "쇼생크 탈출", "인셉션", "라라랜드"]
    else:
        title_pools["matched"] = [f"{db_title} 항목 {i + 1}" for i in range(5)]

    pool = title_pools.get("matched", title_pools["default"])
    available = [t for t in pool if t not in existing_titles]
    if len(available) < count:
        available.extend([f"{db_title} {i + 1}" for i in range(count)])

    statuses = ["시작 전", "진행 중", "완료"]

    items: list[dict[str, Any]] = []
    base_date = datetime.now()

    for idx in range(count):
        item: dict[str, Any] = {}
        title_val = available[idx] if idx < len(available) else f"항목 {len(existing) + idx + 1}"

        for key, spec in props.items():
            ptype = spec if isinstance(spec, str) else spec.get("type", "") if isinstance(spec, dict) else ""

            if ptype == "title":
                item[key] = title_val
            elif ptype == "status":
                item[key] = statuses[idx % len(statuses)]
            elif ptype == "select":
                options = []
                if isinstance(spec, dict):
                    options = [o.get("name", o) if isinstance(o, dict) else o for o in spec.get("options", [])]
                if options:
                    item[key] = options[idx % len(options)]
                else:
                    item[key] = f"카테고리 {idx + 1}"
            elif ptype == "multi_select":
                item[key] = f"태그{idx + 1}"
            elif ptype == "date":
                d = base_date + timedelta(days=idx * 3 - 3)
                item[key] = d.strftime("%Y-%m-%d")
            elif ptype == "number":
                item[key] = (idx + 1) * 10 + random.randint(0, 9)
            elif ptype == "checkbox":
                item[key] = idx % 2 == 0
            elif ptype == "url":
                item[key] = f"https://example.com/{title_val.replace(' ', '-').lower()}"
            elif ptype == "email":
                item[key] = f"user{idx + 1}@example.com"
            elif ptype == "rich_text":
                item[key] = f"{title_val} 관련 메모"
            elif ptype in ("relation", "rollup", "formula"):
                pass

        if title_key not in item:
            item[title_key] = title_val

        items.append(item)

    return items


# 싱글턴
blueprint_validator = BlueprintValidator()
