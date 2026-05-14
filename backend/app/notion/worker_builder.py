"""Notion Workers TypeScript 코드 생성 빌더

Worker 타입별 TypeScript 프로젝트 scaffold + 코드 생성:
- Sync Worker: 외부 데이터 소스 → Notion DB 동기화
- Tool Worker: 사용자가 Notion 내에서 실행하는 커스텀 액션
- Webhook Worker: 이벤트 기반 자동화 (DB 변경, 페이지 생성 등)
"""

from typing import Any


def build_sync_worker(
    name: str,
    source_description: str = "",
    properties: dict[str, str] | None = None,
    schedule: str = "*/15 * * * *",
) -> dict[str, Any]:
    """Sync Worker TypeScript 코드 생성

    properties: {"Name": "title", "Status": "select", ...}
    schedule: cron 표현식
    """
    prop_lines = ""
    if properties:
        prop_lines = "\n".join(f'        "{k}": {{ type: "{v}" }},' for k, v in properties.items())

    code = f'''import {{ defineSyncWorker }} from "@notionhq/workers";

export default defineSyncWorker({{
  name: "{name}",
  schedule: "{schedule}",

  async fetchExternalData(ctx) {{
    // {source_description or "외부 API에서 데이터 가져오기"}
    const response = await fetch("https://api.example.com/data", {{
      headers: {{ "Authorization": `Bearer ${{ctx.env.API_KEY}}` }},
    }});
    return await response.json();
  }},

  mapToProperties(item) {{
    return {{
{prop_lines or '      "Name": { title: [{ text: { content: item.name } }] },'}
    }};
  }},

  getExternalId(item) {{
    return item.id;
  }},
}});
'''

    return {
        "type": "sync",
        "name": name,
        "code": code,
        "schedule": schedule,
        "config": _build_package_json(name, "sync"),
    }


def build_tool_worker(
    name: str,
    description: str = "",
    parameters: dict[str, dict[str, str]] | None = None,
    action_code: str = "",
) -> dict[str, Any]:
    """Tool Worker TypeScript 코드 생성

    parameters: {"query": {"type": "string", "description": "검색어"}, ...}
    """
    param_schema_lines = ""
    if parameters:
        param_schema_lines = "\n".join(
            f'    {k}: {{ type: "{v.get("type", "string")}", description: "{v.get("description", k)}" }},'
            for k, v in parameters.items()
        )

    code = f'''import {{ defineToolWorker }} from "@notionhq/workers";

export default defineToolWorker({{
  name: "{name}",
  description: "{description or name}",

  parameters: {{
{param_schema_lines or '    input: { type: "string", description: "입력값" },'}
  }},

  async execute(ctx, params) {{
{
        action_code
        or """    // 도구 로직 구현
    const result = await ctx.notion.pages.create({
      parent: { page_id: ctx.pageId },
      properties: {
        title: [{ text: { content: `Result: ${params.input}` } }],
      },
    });
    return { success: true, pageId: result.id };"""
    }
  }},
}});
'''

    return {
        "type": "tool",
        "name": name,
        "code": code,
        "description": description,
        "config": _build_package_json(name, "tool"),
    }


def build_webhook_worker(
    name: str,
    event_type: str = "page.created",
    database_id: str = "",
    action_code: str = "",
) -> dict[str, Any]:
    """Webhook Worker TypeScript 코드 생성

    event_type: page.created, page.updated, database.item.created, etc.
    """
    filter_line = ""
    if database_id:
        filter_line = f'\n  filter: {{ database_id: "{database_id}" }},'

    code = f'''import {{ defineWebhookWorker }} from "@notionhq/workers";

export default defineWebhookWorker({{
  name: "{name}",
  event: "{event_type}",{filter_line}

  async handle(ctx, event) {{
{
        action_code
        or """    // 이벤트 핸들러 구현
    console.log(`Event received: ${event.type}`, event.payload);

    if (event.type === "page.created") {
      const pageId = event.payload.page.id;
      await ctx.notion.comments.create({
        parent: { page_id: pageId },
        rich_text: [{ text: { content: "자동 처리 완료!" } }],
      });
    }"""
    }
  }},
}});
'''

    return {
        "type": "webhook",
        "name": name,
        "code": code,
        "event_type": event_type,
        "config": _build_package_json(name, "webhook"),
    }


def build_worker_project(
    workers: list[dict[str, Any]],
    project_name: str = "notionforge-workers",
) -> dict[str, Any]:
    """여러 Worker를 포함하는 프로젝트 scaffold 생성"""
    files: dict[str, str] = {}

    files["package.json"] = _build_root_package_json(project_name, workers)
    files["tsconfig.json"] = _build_tsconfig()
    files["notion.config.ts"] = _build_notion_config(workers)

    for w in workers:
        filename = f"src/{w['name'].replace(' ', '_').lower()}.ts"
        files[filename] = w["code"]

    files[".env.example"] = "NOTION_API_KEY=ntn_xxx\n"
    files[".gitignore"] = "node_modules/\ndist/\n.env\n"

    return {
        "project_name": project_name,
        "files": files,
        "workers": [{"name": w["name"], "type": w["type"]} for w in workers],
    }


def _build_package_json(name: str, worker_type: str) -> dict[str, Any]:
    return {
        "name": name.replace(" ", "-").lower(),
        "type": "module",
        "dependencies": {
            "@notionhq/workers": "^1.0.0",
        },
        "devDependencies": {
            "typescript": "^5.7.0",
        },
        "scripts": {
            "dev": "ntn dev",
            "deploy": "ntn deploy",
            "logs": "ntn logs",
        },
    }


def _build_root_package_json(project_name: str, workers: list[dict]) -> str:
    worker_names = ", ".join(f'"{w["name"]}"' for w in workers)
    return f'''{{
  "name": "{project_name}",
  "private": true,
  "type": "module",
  "scripts": {{
    "dev": "ntn dev",
    "deploy": "ntn deploy",
    "logs": "ntn logs",
    "typecheck": "tsc --noEmit"
  }},
  "dependencies": {{
    "@notionhq/workers": "^1.0.0"
  }},
  "devDependencies": {{
    "typescript": "^5.7.0",
    "@types/node": "^22.0.0"
  }},
  "notion": {{
    "workers": [{worker_names}]
  }}
}}
'''


def _build_tsconfig() -> str:
    return """{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "outDir": "dist",
    "rootDir": "src",
    "declaration": true,
    "resolveJsonModule": true
  },
  "include": ["src/**/*.ts"],
  "exclude": ["node_modules", "dist"]
}
"""


def _build_notion_config(workers: list[dict]) -> str:
    worker_imports = "\n".join(
        f'import {w["name"].replace(" ", "_").replace("-", "_")} from "./src/{w["name"].replace(" ", "_").lower()}";'
        for w in workers
    )
    worker_refs = ", ".join(w["name"].replace(" ", "_").replace("-", "_") for w in workers)

    return f"""import {{ defineConfig }} from "@notionhq/workers";
{worker_imports}

export default defineConfig({{
  workers: [{worker_refs}],
}});
"""
