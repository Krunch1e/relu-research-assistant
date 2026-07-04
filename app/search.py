import httpx
from app.config import settings

SERPER_URL = "https://google.serper.dev/search"

async def serper_search(query: str, num: int = 10) -> dict:
    if not settings.SERPER_API_KEY:
        raise ValueError("SERPER_API_KEY is missing. Check your .env file.")
    headers = {"X-API-KEY": settings.SERPER_API_KEY, "Content-Type": "application/json"}
    payload = {"q": query, "num": num}
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(SERPER_URL, json=payload, headers=headers)
        resp.raise_for_status()
        return resp.json()

async def find_official_website(company_name: str) -> str | None:
    data = await serper_search(f"{company_name} company official website")
    organic = data.get("organic", [])
    # Heuristic: skip aggregator/social domains
    blocklist = ["linkedin.com", "wikipedia.org", "crunchbase.com", "facebook.com", "twitter.com", "x.com", "instagram.com", "youtube.com"]
    for result in organic:
        link = result.get("link", "")
        if not any(b in link for b in blocklist):
            return link
    return organic[0]["link"] if organic else None
