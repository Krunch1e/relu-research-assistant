import httpx
import json
from app.config import settings

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

async def call_openrouter(prompt: str, model: str) -> str:
    if not settings.OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY is missing. Check your .env file.")
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
    }
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(OPENROUTER_URL, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]


PROFILE_PROMPT = """You are a company research analyst. Based on the following
website content, extract and infer the following fields. Respond ONLY with valid
JSON, no markdown fences, no preamble.

Website content:
{content}

Return JSON with exactly these keys:
{{
  "company_name": "string",
  "phone": "string or null",
  "address": "string or null",
  "products_services": ["string", "..."],
  "pain_points": ["string", "..."],
  "summary": "Detailed executive summary. Use multiple distinct paragraphs separated by newlines (\\n). Include history, business model, and market position."
}}
"""

async def generate_company_profile(content: str, model: str) -> dict:
    prompt = PROFILE_PROMPT.format(content=content[:12000])
    raw = await call_openrouter(prompt, model)
    cleaned = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(cleaned)
