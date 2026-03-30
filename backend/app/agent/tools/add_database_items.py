"""DB에 샘플 항목 추가 -- 실제 속성명 자동 매핑 (퍼지 매칭 포함)"""

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

        # Notion에서 실제 DB 속성명 조회
        real_props = await self._get_real_property_map(database_id)

        # blueprint 속성명 -> 실제 속성명 매핑 테이블 구축
        prop_name_map = _build_property_name_map(db_properties, real_props)

        results = []
        for item in items:
            try:
                props = _build_item_props(item, db_properties, real_props, prop_name_map)
                if not props:
                    continue
                result = await self.client.add_database_item(
                    database_id=database_id,
                    properties=props,
                    icon=item.get("icon"),
                    cover_url=item.get("cover_url"),
                )
                results.append(result)
            except Exception as e:
                print(f"[샘플 항목 스킵] {str(e)[:80]}")
                continue
        return {"item_count": len(results), "results": results}

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
            return real_props
        except Exception:
            return {}


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

    # 3단계: 남은 속성 퍼지 매칭 (같은 타입끼리, 유사도 0.4 이상)
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
        if best_match and best_score >= 0.4:
            name_map[bname] = best_match
            used_real.add(best_match)

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
            actual_type = real_props[actual_key]["type"]
        elif key in real_props:
            # 매핑 테이블에 없지만 실제 DB에 직접 존재
            actual_key = key
            actual_type = real_props[key]["type"]
        elif bp_type == "title" and real_title_key:
            # title 타입인데 이름이 다름 -> 실제 title 속성명 사용
            actual_key = real_title_key
            actual_type = "title"
        else:
            # 실제 DB에 없는 속성 -> 스킵
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
        return {"status": {"name": str(value)}}
    elif prop_type == "checkbox":
        return {"checkbox": bool(value)}
    elif prop_type == "number":
        try:
            return {"number": float(value) if value is not None else None}
        except (ValueError, TypeError):
            return {"number": None}
    elif prop_type == "url":
        return {"url": str(value) if value else None}
    elif prop_type == "email":
        return {"email": str(value) if value else None}
    elif prop_type == "date":
        if value:
            return {"date": {"start": str(value)}}
        return {"date": None}
    elif prop_type == "people":
        # people은 user ID가 필요한데 AI는 문자열 이름을 생성함 → rich_text로 폴백
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
