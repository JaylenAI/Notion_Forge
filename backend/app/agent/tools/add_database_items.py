"""DB에 샘플 항목 추가 -- 실제 속성명 자동 매핑 (퍼지 매칭 포함)"""

import logging

logger = logging.getLogger("notionforge.add_database_items")

import asyncio
from difflib import SequenceMatcher
from typing import Any

from app.agent.tools.base import BaseTool
from app.notion.client import NotionClient


class AddDatabaseItemsTool(BaseTool):
    name = "add_database_items"
    description = "데이터베이스에 샘플 항목을 추가합니다"

    def __init__(self, client: NotionClient):
        self.client = client

    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        database_id = kwargs["database_id"]
        items = kwargs["items"]
        db_properties = kwargs.get("db_properties", {})

        # DB 생성 직후 속성이 아직 반영 안 될 수 있으므로 잠시 대기 후 조회
        await asyncio.sleep(0.5)

        # Notion에서 실제 DB 속성명 조회 (최대 2회 시도)
        real_props = await self._get_real_property_map(database_id)
        if not real_props:
            await asyncio.sleep(1.0)
            real_props = await self._get_real_property_map(database_id)

        if not real_props:
            logger.info(f"[샘플 데이터] 실제 DB 속성을 조회할 수 없음 → blueprint 속성으로 폴백")
            # blueprint 속성을 real_props 형태로 변환해서 사용
            real_props = _blueprint_to_real_props(db_properties)

        # blueprint 속성명 -> 실제 속성명 매핑 테이블 구축
        prop_name_map = _build_property_name_map(db_properties, real_props)
        logger.info(f"[샘플 데이터] 속성 매핑: {prop_name_map}")

        results = []
        errors = []
        for i, item in enumerate(items):
            try:
                props = _build_item_props(item, db_properties, real_props, prop_name_map)
                if not props:
                    logger.info(f"[샘플 항목 {i+1}] 속성 변환 결과 비어있음, 스킵")
                    continue
                result = await self.client.add_database_item(
                    database_id=database_id,
                    properties=props,
                    icon=item.get("icon"),
                    cover_url=item.get("cover_url"),
                )
                results.append(result)
            except Exception as e:
                err_msg = str(e)[:120]
                errors.append(err_msg)
                logger.info(f"[샘플 항목 {i+1} 실패] {err_msg}")
                continue

        logger.info(f"[샘플 데이터] 결과: {len(results)}/{len(items)} 성공, {len(errors)} 실패")
        return {"item_count": len(results), "results": results, "errors": errors}

    async def _get_real_property_map(self, database_id: str) -> dict[str, dict]:
        """Notion DB에서 실제 속성 이름과 타입 조회"""
        try:
            db_info = await self.client.get_database(database_id)
            real_props = {}
            for prop_name, prop_data in db_info.get("properties", {}).items():
                real_props[prop_name] = {
                    "type": prop_data.get("type", "rich_text"),
                    "id": prop_data.get("id", ""),
                }
            logger.info(f"[샘플 데이터] 실제 DB 속성 {len(real_props)}개 조회됨: {list(real_props.keys())}")
            return real_props
        except Exception as e:
            logger.info(f"[샘플 데이터] DB 속성 조회 실패: {e}")
            return {}


def _blueprint_to_real_props(db_properties: dict) -> dict[str, dict]:
    """blueprint 속성 스펙을 real_props 형태로 변환 (폴백용)"""
    result = {}
    for name, spec in db_properties.items():
        if spec == "title" or (isinstance(spec, dict) and spec.get("type") == "title"):
            result[name] = {"type": "title", "id": "title"}
        elif isinstance(spec, str):
            result[name] = {"type": spec, "id": ""}
        elif isinstance(spec, dict):
            result[name] = {"type": spec.get("type", "rich_text"), "id": ""}
        else:
            result[name] = {"type": "rich_text", "id": ""}
    return result


def _build_property_name_map(
    blueprint_props: dict, real_props: dict
) -> dict[str, str]:
    """blueprint 속성명 -> 실제 Notion 속성명 매핑 테이블 생성.

    1단계: 정확히 일치하는 이름
    2단계: 타입이 같은 속성끼리 퍼지 매칭
    3단계: title 타입은 이름이 달라도 무조건 매핑
    """
    name_map: dict[str, str] = {}
    used_real: set[str] = set()

    # 실제 DB에서 title 속성 찾기
    real_title_key: str | None = None
    for rname, rinfo in real_props.items():
        if rinfo.get("type") == "title":
            real_title_key = rname
            break

    # blueprint에서 각 속성의 타입 추출
    bp_types: dict[str, str] = {}
    for bname, bspec in blueprint_props.items():
        if bspec == "title" or (isinstance(bspec, dict) and bspec.get("type") == "title"):
            bp_types[bname] = "title"
        elif isinstance(bspec, str):
            bp_types[bname] = bspec
        elif isinstance(bspec, dict):
            bp_types[bname] = bspec.get("type", "rich_text")
        else:
            bp_types[bname] = "rich_text"

    # 1단계: 정확히 일치
    for bname in blueprint_props:
        if bname in real_props:
            name_map[bname] = bname
            used_real.add(bname)

    # 2단계: title 타입 강제 매핑
    for bname, btype in bp_types.items():
        if bname in name_map:
            continue
        if btype == "title" and real_title_key and real_title_key not in used_real:
            name_map[bname] = real_title_key
            used_real.add(real_title_key)

    # 3단계: 남은 속성 퍼지 매칭 (같은 타입끼리, 유사도 0.3 이상으로 낮춤)
    for bname, btype in bp_types.items():
        if bname in name_map:
            continue
        best_match: str | None = None
        best_score = 0.0
        for rname, rinfo in real_props.items():
            if rname in used_real:
                continue
            if rinfo.get("type") != btype:
                continue
            score = _similarity(bname, rname)
            if score > best_score:
                best_score = score
                best_match = rname
        if best_match and best_score >= 0.3:
            name_map[bname] = best_match
            used_real.add(best_match)

    # 4단계: 타입이 같은데 매핑 안 된 속성 → 순서대로 매핑
    for bname, btype in bp_types.items():
        if bname in name_map:
            continue
        for rname, rinfo in real_props.items():
            if rname in used_real:
                continue
            if rinfo.get("type") == btype:
                name_map[bname] = rname
                used_real.add(rname)
                break

    return name_map


def _similarity(a: str, b: str) -> float:
    """두 문자열의 유사도 (0~1)"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def _build_item_props(
    item: dict,
    blueprint_props: dict,
    real_props: dict,
    prop_name_map: dict[str, str],
) -> dict[str, Any]:
    """샘플 항목 -> Notion 속성 형식. 실제 DB 속성명으로 매핑."""
    properties: dict[str, Any] = {}

    # 실제 DB에서 title 속성 이름 찾기 (fallback용)
    real_title_key: str | None = None
    for name, info in real_props.items():
        if info.get("type") == "title":
            real_title_key = name
            break

    for key, value in item.items():
        if key in ("icon", "cover_url"):
            continue

        # 1. blueprint에서 이 키의 타입 확인
        bp_spec = blueprint_props.get(key)
        bp_type: str | None = None
        if bp_spec == "title":
            bp_type = "title"
        elif isinstance(bp_spec, str):
            bp_type = bp_spec
        elif isinstance(bp_spec, dict):
            bp_type = bp_spec.get("type")

        # 2. 매핑 테이블에서 실제 속성명 찾기
        if key in prop_name_map:
            actual_key = prop_name_map[key]
            actual_type = real_props.get(actual_key, {}).get("type", bp_type or "rich_text")
        elif key in real_props:
            actual_key = key
            actual_type = real_props[key]["type"]
        elif bp_type == "title" and real_title_key:
            actual_key = real_title_key
            actual_type = "title"
        else:
            # 실제 DB에 없는 속성 → 스킵하지 않고, blueprint 타입으로 시도
            if bp_type:
                actual_key = key
                actual_type = bp_type
            else:
                continue

        # 3. 타입에 맞게 값 변환
        properties[actual_key] = _format_value(actual_type, value)

    # title 속성이 하나도 없으면, 첫 번째 값을 title로 넣기
    if real_title_key and real_title_key not in properties:
        first_value = next(
            (v for k, v in item.items() if k not in ("icon", "cover_url")),
            None,
        )
        if first_value is not None:
            properties[real_title_key] = _format_value("title", first_value)

    return properties


def _format_value(prop_type: str, value: Any) -> dict[str, Any]:
    """속성 타입에 맞게 값을 Notion API 형식으로 변환"""
    if prop_type == "title":
        return {"title": [{"text": {"content": str(value)}}]}
    elif prop_type == "rich_text":
        return {"rich_text": [{"text": {"content": str(value)}}]}
    elif prop_type == "select":
        return {"select": {"name": str(value)}}
    elif prop_type == "multi_select":
        names = value if isinstance(value, list) else [str(value)]
        return {"multi_select": [{"name": n} for n in names]}
    elif prop_type == "status":
        # Notion status 속성은 기본 옵션이 영어: Not started, In progress, Done
        # AI가 한국어로 생성하면 매핑 필요
        status_map = {
            # 기본
            "시작 전": "Not started", "시작전": "Not started", "대기": "Not started",
            "미시작": "Not started", "예정": "Not started", "계획": "Not started",
            "준비": "Not started", "대기 중": "Not started", "대기중": "Not started",
            "진행 중": "In progress", "진행중": "In progress", "진행": "In progress",
            "작업 중": "In progress", "작업중": "In progress", "활성": "In progress",
            "처리 중": "In progress", "처리중": "In progress",
            "완료": "Done", "완료됨": "Done", "끝": "Done", "마감": "Done",
            "종료": "Done", "해결": "Done", "해결됨": "Done",
            # 독서/학습
            "읽기 전": "Not started", "읽기전": "Not started", "미독": "Not started",
            "읽는 중": "In progress", "읽는중": "In progress", "독서 중": "In progress",
            "읽음": "Done", "독서완료": "Done", "다 읽음": "Done",
            "수강 전": "Not started", "수강전": "Not started",
            "수강 중": "In progress", "수강중": "In progress", "학습 중": "In progress",
            "수강 완료": "Done", "수강완료": "Done",
            # 콘텐츠/프로젝트
            "기획": "Not started", "기획 중": "Not started",
            "작성 중": "In progress", "작성중": "In progress", "리뷰": "In progress",
            "리뷰 중": "In progress", "검토 중": "In progress",
            "발행": "Done", "발행됨": "Done", "배포": "Done", "출시": "Done",
            # 영어 (소문자)
            "not started": "Not started", "todo": "Not started", "to do": "Not started",
            "in progress": "In progress", "doing": "In progress", "active": "In progress",
            "done": "Done", "completed": "Done", "finished": "Done",
        }
        mapped = status_map.get(str(value).strip(), str(value))
        return {"status": {"name": mapped}}
    elif prop_type == "checkbox":
        if isinstance(value, bool):
            return {"checkbox": value}
        return {"checkbox": str(value).lower() in ("true", "1", "yes", "✅")}
    elif prop_type == "number":
        try:
            # 숫자에서 콤마, 원, 달러 등 제거
            cleaned = str(value).replace(",", "").replace("원", "").replace("$", "").replace("₩", "").strip()
            return {"number": float(cleaned) if cleaned else None}
        except (ValueError, TypeError):
            return {"number": None}
    elif prop_type == "url":
        return {"url": str(value) if value else None}
    elif prop_type == "email":
        return {"email": str(value) if value else None}
    elif prop_type == "date":
        if value:
            date_str = str(value).strip()
            # 날짜 형식 정리 (YYYY-MM-DD만 허용)
            if len(date_str) >= 10:
                date_str = date_str[:10]
            return {"date": {"start": date_str}}
        return {"date": None}
    elif prop_type == "people":
        if isinstance(value, str) and not value.startswith(("user_", "u_")):
            return {"rich_text": [{"text": {"content": str(value)}}]}
        if isinstance(value, list):
            return {"people": [{"id": uid} for uid in value]}
        return {"people": [{"id": str(value)}]}
    elif prop_type == "files":
        if isinstance(value, list):
            return {"files": [{"type": "external", "name": v, "external": {"url": v}} for v in value]}
        return {"files": [{"type": "external", "name": str(value), "external": {"url": str(value)}}]}
    elif prop_type == "phone_number":
        return {"phone_number": str(value) if value else None}
    elif prop_type == "relation":
        if isinstance(value, list):
            return {"relation": [{"id": rid} for rid in value]}
        return {"relation": [{"id": str(value)}]}
    else:
        return {"rich_text": [{"text": {"content": str(value)}}]}
