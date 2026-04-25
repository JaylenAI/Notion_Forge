"""Document-to-Notion: PDF/텍스트 → 구조 분석 → 템플릿 자동 생성

지원 형식: .txt, .md, .csv (PDF는 PyMuPDF 선택 설치)
"""

import csv
import io
import re
from typing import Any


def parse_document(content: str, filename: str = "") -> dict[str, Any]:
    """문서를 분석하여 블루프린트 힌트를 생성"""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "txt"

    if ext == "csv":
        return _parse_csv(content)
    elif ext == "md":
        return _parse_markdown(content)
    else:
        return _parse_text(content)


def _parse_csv(content: str) -> dict[str, Any]:
    """CSV → 데이터베이스 구조 추출"""
    reader = csv.reader(io.StringIO(content))
    rows = list(reader)
    if not rows:
        return {"hint": "빈 CSV 파일", "properties": {}, "sample_items": []}

    headers = rows[0]
    # 헤더에서 속성 타입 추정
    properties: dict[str, str] = {}
    for h in headers:
        h_lower = h.lower()
        if any(w in h_lower for w in ["이름", "name", "title", "제목"]):
            properties[h] = "title"
        elif any(w in h_lower for w in ["날짜", "date", "일자"]):
            properties[h] = "date"
        elif any(w in h_lower for w in ["금액", "가격", "price", "amount", "수량"]):
            properties[h] = "number"
        elif any(w in h_lower for w in ["상태", "status"]):
            properties[h] = "status"
        elif any(w in h_lower for w in ["이메일", "email"]):
            properties[h] = "email"
        elif any(w in h_lower for w in ["url", "link", "링크"]):
            properties[h] = "url"
        elif any(w in h_lower for w in ["체크", "완료", "done"]):
            properties[h] = "checkbox"
        else:
            properties[h] = "rich_text"

    # 샘플 데이터 (최대 5행)
    sample_items = []
    for row in rows[1:6]:
        item = {}
        for i, val in enumerate(row):
            if i < len(headers):
                item[headers[i]] = val
        sample_items.append(item)

    return {
        "hint": f"CSV 데이터 — {len(headers)}개 컬럼, {len(rows) - 1}개 행",
        "properties": properties,
        "sample_items": sample_items,
        "db_title": "Imported Data",
    }


def _parse_markdown(content: str) -> dict[str, Any]:
    """Markdown → 블록 구조 추출"""
    blocks: list[dict[str, Any]] = []
    lines = content.split("\n")

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        # Headings
        if stripped.startswith("# "):
            blocks.append({"type": "heading_1", "text": stripped[2:]})
        elif stripped.startswith("## "):
            blocks.append({"type": "heading_2", "text": stripped[3:]})
        elif stripped.startswith("### "):
            blocks.append({"type": "heading_3", "text": stripped[4:]})
        # Checkboxes (must be before bulleted list — both start with "- ")
        elif stripped.startswith("- [ ] ") or stripped.startswith("- [x] "):
            checked = stripped.startswith("- [x] ")
            blocks.append({"type": "to_do", "text": stripped[6:], "checked": checked})
        # Lists
        elif stripped.startswith("- ") or stripped.startswith("* "):
            blocks.append({"type": "bulleted_list", "text": stripped[2:]})
        elif re.match(r"^\d+\.\s", stripped):
            blocks.append({"type": "numbered_list", "text": re.sub(r"^\d+\.\s", "", stripped)})
        # Blockquotes
        elif stripped.startswith("> "):
            blocks.append({"type": "quote", "text": stripped[2:]})
        # Code blocks
        elif stripped.startswith("```"):
            blocks.append({"type": "divider"})
        # Horizontal rule
        elif stripped in ("---", "***", "___"):
            blocks.append({"type": "divider"})
        # Regular paragraph
        else:
            blocks.append({"type": "paragraph", "text": stripped})

    return {
        "hint": f"Markdown 문서 — {len(blocks)}개 블록",
        "blocks": blocks,
    }


def _parse_text(content: str) -> dict[str, Any]:
    """일반 텍스트 → 구조 추출"""
    lines = [line.strip() for line in content.split("\n") if line.strip()]

    # 텍스트를 AI에게 전달할 컨텍스트로 요약
    summary = "\n".join(lines[:30])  # 최대 30줄
    return {
        "hint": f"텍스트 문서 — {len(lines)}줄",
        "text_content": summary,
    }


def parse_pdf_bytes(pdf_bytes: bytes) -> dict[str, Any]:
    """PDF 바이트 → 텍스트 추출 (PyMuPDF 선택 설치)"""
    try:
        import fitz  # PyMuPDF

        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return _parse_text(text)
    except ImportError:
        return {
            "hint": "PDF 파싱에는 PyMuPDF가 필요합니다 (pip install pymupdf)",
            "text_content": "",
        }
    except Exception as e:
        return {
            "hint": f"PDF 파싱 실패: {str(e)[:100]}",
            "text_content": "",
        }
