from app.search import serper_search
from app.ai import call_openrouter
import json

async def find_competitors(company_name: str, industry_hint: str, model: str) -> list[dict]:
    data = await serper_search(f"{company_name} competitors alternatives")
    organic = data.get("organic", [])[:8]
    raw_list = "\n".join(f"- {r.get('title')}: {r.get('link')}" for r in organic)

    prompt = f"""From the following search results about competitors of
{company_name} (industry: {industry_hint}), extract a clean list of DISTINCT
competitor companies (not {company_name} itself, not review sites, not
listicle articles). Respond ONLY with a JSON array like
[{{"name": "...", "website": "..."}}], max 5 entries. No markdown fences.

Search results:
{raw_list}
"""
    try:
        raw = await call_openrouter(prompt, model)
        cleaned = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        return json.loads(cleaned)
    except Exception as e:
        print(f"Failed to find competitors: {e}")
        return []
