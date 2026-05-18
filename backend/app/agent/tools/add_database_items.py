"""DB에 샘플 항목 추가 -- 실제 속성명 자동 매핑 (퍼지 매칭 + 직접 매핑 포함)"""

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
    parameters = {
        "database_id": {"type": "string", "description": "대상 DB ID"},
        "items": {"type": "array", "description": "항목 배열 [{속성명: 값, ...}]"},
        "db_properties": {"type": "object", "description": "DB 속성 정의 (매핑용)", "optional": True},
    }

    def __init__(self, client: NotionClient):
        self.client = client

    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        database_id = kwargs["database_id"]
        items = kwargs["items"]
        db_properties = kwargs.get("db_properties", {})

        await asyncio.sleep(0.5)

        real_props = await self._get_real_property_map(database_id)
        if not real_props:
            await asyncio.sleep(1.0)
            real_props = await self._get_real_property_map(database_id)

        if not real_props:
            logger.info("[샘플 데이터] 실제 DB 속성을 조회할 수 없음 → blueprint 속성으로 폴백")
            real_props = _blueprint_to_real_props(db_properties)

        prop_name_map = _build_property_name_map(db_properties, real_props)

        all_sample_keys: set[str] = set()
        for item in items:
            all_sample_keys.update(k for k in item.keys() if k not in ("icon", "cover_url"))
        sample_direct_map = _build_sample_key_direct_map(all_sample_keys, db_properties, real_props, prop_name_map)
        prop_name_map.update(sample_direct_map)

        logger.info(f"[샘플 데이터] 최종 속성 매핑: {prop_name_map}")
        logger.info(f"[샘플 데이터] 실제 DB 속성: {list(real_props.keys())}")

        results = []
        errors = []
        for i, item in enumerate(items):
            try:
                props = _build_item_props(item, db_properties, real_props, prop_name_map)
                if not props:
                    logger.info(f"[샘플 항목 {i + 1}] 속성 변환 결과 비어있음, 스킵")
                    continue
                result = await self.client.add_database_item(
                    database_id=database_id,
                    properties=props,
                    icon=item.get("icon"),
                    cover_url=item.get("cover_url"),
                )
                results.append(result)
            except Exception as e:
                err_msg = str(e)[:200]
                errors.append(err_msg)
                logger.info(f"[샘플 항목 {i + 1} 실패] {err_msg}")
                try:
                    title_props = _build_title_only_props(item, real_props, prop_name_map)
                    if title_props:
                        result = await self.client.add_database_item(
                            database_id=database_id,
                            properties=title_props,
                            icon=item.get("icon"),
                        )
                        results.append(result)
                        logger.info(f"[샘플 항목 {i + 1}] title만으로 재시도 성공")
                except Exception:
                    pass

        logger.info(f"[샘플 데이터] 결과: {len(results)}/{len(items)} 성공, {len(errors)} 실패")
        return {"item_count": len(results), "results": results, "errors": errors}

    async def _get_real_property_map(self, database_id: str) -> dict[str, dict]:
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


def _get_bp_type(spec: Any) -> str:
    if spec == "title" or (isinstance(spec, dict) and spec.get("type") == "title"):
        return "title"
    if isinstance(spec, str):
        return spec
    if isinstance(spec, dict):
        return spec.get("type", "rich_text")
    return "rich_text"


def _build_property_name_map(blueprint_props: dict, real_props: dict) -> dict[str, str]:
    """blueprint 속성명 -> 실제 Notion 속성명 매핑 테이블 생성."""
    name_map: dict[str, str] = {}
    used_real: set[str] = set()

    real_title_key: str | None = None
    for rname, rinfo in real_props.items():
        if rinfo.get("type") == "title":
            real_title_key = rname
            break

    bp_types: dict[str, str] = {}
    for bname, bspec in blueprint_props.items():
        bp_types[bname] = _get_bp_type(bspec)

    for bname in blueprint_props:
        if bname in real_props:
            name_map[bname] = bname
            used_real.add(bname)

    for bname, btype in bp_types.items():
        if bname in name_map:
            continue
        if btype == "title" and real_title_key and real_title_key not in used_real:
            name_map[bname] = real_title_key
            used_real.add(real_title_key)

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


def _build_sample_key_direct_map(
    sample_keys: set[str],
    blueprint_props: dict,
    real_props: dict[str, dict],
    existing_map: dict[str, str],
) -> dict[str, str]:
    """샘플 아이템 키 → 실제 DB 속성 직접 매핑 (prop_name_map에 없는 키 처리)

    existing_map은 blueprint 키 → real 속성 매핑이므로,
    sample 키는 같은 real 속성에 독립적으로 매핑할 수 있다.
    (sample 키끼리만 중복 방지)
    """
    result: dict[str, str] = {}
    used_real: set[str] = set()

    real_title_key: str | None = None
    for rname, rinfo in real_props.items():
        if rinfo.get("type") == "title":
            real_title_key = rname
            break

    for skey in sample_keys:
        if skey in existing_map or skey in result:
            continue
        if skey in real_props:
            result[skey] = skey
            used_real.add(skey)

    title_hints = {
        "이름",
        "name",
        "제목",
        "title",
        "태스크",
        "태스크명",
        "항목",
        "항목명",
        "작업",
        "작업명",
        "자료명",
        "문서명",
        "프로젝트명",
        "프로젝트",
        "일정",
        "일정명",
        "회의명",
    }
    if real_title_key:
        for skey in sample_keys:
            if skey in existing_map or skey in result:
                continue
            if skey.lower() in title_hints or any(h in skey.lower() for h in ("이름", "name", "제목", "title")):
                result[skey] = real_title_key
                used_real.add(real_title_key)
                break

    for skey in sample_keys:
        if skey in existing_map or skey in result:
            continue
        best_match: str | None = None
        best_score = 0.0
        for rname in real_props:
            if rname in used_real:
                continue
            score = _similarity(skey, rname)
            if score > best_score:
                best_score = score
                best_match = rname
        if best_match and best_score >= 0.4:
            result[skey] = best_match
            used_real.add(best_match)

    for skey in sample_keys:
        if skey in existing_map or skey in result:
            continue
        bp_spec = blueprint_props.get(skey)
        if bp_spec is None:
            continue
        skey_type = _get_bp_type(bp_spec)
        if skey_type == "title" and real_title_key and real_title_key not in used_real:
            result[skey] = real_title_key
            used_real.add(real_title_key)
            continue
        for rname, rinfo in real_props.items():
            if rname in used_real:
                continue
            if rinfo.get("type") == skey_type:
                result[skey] = rname
                used_real.add(rname)
                break

    return result


_KOREAN_SYNONYMS: dict[str, set[str]] = {
    "날짜": {"마감일", "기한", "마감", "일정", "기간", "시작일", "종료일", "생성일", "일자"},
    "마감일": {"날짜", "기한", "마감", "일정", "기간", "일자"},
    "기한": {"마감일", "날짜", "마감", "기간"},
    "일정": {"날짜", "마감일", "기한", "기간"},
    "이름": {"태스크명", "제목", "항목명", "작업명", "자료명", "문서명", "프로젝트명", "회의명"},
    "제목": {"이름", "태스크명", "항목명", "작업명", "자료명"},
    "태스크명": {"이름", "제목", "항목명", "작업명"},
    "항목명": {"이름", "제목", "태스크명"},
    "담당자": {"담당", "책임자", "배정", "소유자", "작성자", "팀원", "멤버"},
    "담당": {"담당자", "책임자", "배정", "멤버"},
    "역할": {"담당", "담당자", "포지션"},
    "상태": {"진행상태", "진행 상태", "현황", "스테이터스"},
    "우선순위": {"중요도", "긴급도", "우선도"},
    "카테고리": {"분류", "종류", "유형", "타입", "구분"},
    "분류": {"카테고리", "종류", "유형", "타입", "구분"},
    "설명": {"내용", "메모", "비고", "노트", "상세", "세부사항", "디스크립션"},
    "내용": {"설명", "메모", "비고", "노트", "상세"},
    "메모": {"설명", "내용", "비고", "노트"},
    "링크": {"URL", "주소", "웹", "사이트", "경로"},
    "태그": {"라벨", "레이블", "분류"},
}


def _similarity(a: str, b: str) -> float:
    al, bl = a.lower(), b.lower()
    seq_score = SequenceMatcher(None, al, bl).ratio()
    synonyms = _KOREAN_SYNONYMS.get(al, set())
    if bl in synonyms or al in _KOREAN_SYNONYMS.get(bl, set()):
        return max(seq_score, 0.85)
    return seq_score


def _build_item_props(
    item: dict,
    blueprint_props: dict,
    real_props: dict,
    prop_name_map: dict[str, str],
) -> dict[str, Any]:
    """샘플 항목 -> Notion 속성 형식. 실제 DB에 존재하는 속성만 포함."""
    properties: dict[str, Any] = {}

    real_title_key: str | None = None
    for name, info in real_props.items():
        if info.get("type") == "title":
            real_title_key = name
            break

    for key, value in item.items():
        if key in ("icon", "cover_url"):
            continue

        if key in prop_name_map:
            actual_key = prop_name_map[key]
            actual_type = real_props.get(actual_key, {}).get("type", "rich_text")
        elif key in real_props:
            actual_key = key
            actual_type = real_props[key]["type"]
        else:
            bp_spec = blueprint_props.get(key)
            bp_type = _get_bp_type(bp_spec) if bp_spec is not None else None
            if bp_type == "title" and real_title_key:
                actual_key = real_title_key
                actual_type = "title"
            else:
                continue

        if actual_key not in real_props:
            continue

        properties[actual_key] = _format_value(actual_type, value)

    if real_title_key and real_title_key not in properties:
        first_value = next(
            (v for k, v in item.items() if k not in ("icon", "cover_url") and v),
            None,
        )
        if first_value is not None:
            properties[real_title_key] = _format_value("title", first_value)

    return properties


def _build_title_only_props(
    item: dict,
    real_props: dict[str, dict],
    prop_name_map: dict[str, str],
) -> dict[str, Any]:
    """실패 시 title 속성만으로 최소 항목 생성"""
    real_title_key = next((rn for rn, ri in real_props.items() if ri.get("type") == "title"), None)
    if not real_title_key:
        return {}

    title_value = None
    for key, value in item.items():
        if key in ("icon", "cover_url"):
            continue
        mapped = prop_name_map.get(key, key)
        if mapped == real_title_key:
            title_value = str(value)
            break

    if not title_value:
        title_value = next(
            (str(v) for k, v in item.items() if k not in ("icon", "cover_url") and v),
            "항목",
        )

    return {real_title_key: {"title": [{"text": {"content": title_value}}]}}


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
        status_map = {
            "not started": "시작 전",
            "todo": "시작 전",
            "to do": "시작 전",
            "Not started": "시작 전",
            "TODO": "시작 전",
            "in progress": "진행 중",
            "doing": "진행 중",
            "active": "진행 중",
            "In progress": "진행 중",
            "done": "완료",
            "completed": "완료",
            "finished": "완료",
            "Done": "완료",
            "Completed": "완료",
            "시작전": "시작 전",
            "대기": "시작 전",
            "미시작": "시작 전",
            "예정": "시작 전",
            "계획": "시작 전",
            "준비": "시작 전",
            "대기 중": "시작 전",
            "대기중": "시작 전",
            "진행중": "진행 중",
            "진행": "진행 중",
            "작업 중": "진행 중",
            "작업중": "진행 중",
            "처리 중": "진행 중",
            "처리중": "진행 중",
            "활성": "진행 중",
            "완료됨": "완료",
            "끝": "완료",
            "마감": "완료",
            "종료": "완료",
            "해결": "완료",
            "해결됨": "완료",
            "읽기 전": "시작 전",
            "읽기전": "시작 전",
            "미독": "시작 전",
            "읽는 중": "진행 중",
            "읽는중": "진행 중",
            "독서 중": "진행 중",
            "읽음": "완료",
            "독서완료": "완료",
            "다 읽음": "완료",
            "수강 전": "시작 전",
            "수강전": "시작 전",
            "수강 중": "진행 중",
            "수강중": "진행 중",
            "학습 중": "진행 중",
            "수강 완료": "완료",
            "수강완료": "완료",
            "기획": "시작 전",
            "기획 중": "시작 전",
            "작성 중": "진행 중",
            "작성중": "진행 중",
            "리뷰": "진행 중",
            "리뷰 중": "진행 중",
            "검토 중": "진행 중",
            "발행": "완료",
            "발행됨": "완료",
            "배포": "완료",
            "출시": "완료",
        }
        mapped = status_map.get(str(value).strip(), str(value).strip())
        return {"status": {"name": mapped}}
    elif prop_type == "checkbox":
        if isinstance(value, bool):
            return {"checkbox": value}
        return {"checkbox": str(value).lower() in ("true", "1", "yes", "✅")}
    elif prop_type == "number":
        try:
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
