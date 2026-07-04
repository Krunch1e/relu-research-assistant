import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

TARGET_KEYWORDS = ["about", "product", "service", "solution", "contact", "pricing", "plans"]
SKIP_KEYWORDS = ["login", "signin", "sign-in", "register", "signup", "sign-up",
                 "cart", "checkout", "privacy", "terms", "cookie"]

async def crawl_site(base_url: str, max_pages: int = 8) -> dict[str, str]:
    """Returns {url: extracted_text} for home + relevant discovered pages."""
    visited = set()
    pages_content = {}

    async with httpx.AsyncClient(timeout=10, follow_redirects=True,
                                  headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}) as client:
        # 1. Fetch homepage
        home_html = await _fetch(client, base_url)
        if not home_html:
            return pages_content
        pages_content[base_url] = _extract_text(home_html)
        visited.add(_normalize(base_url))

        # 2. Discover internal links from homepage
        links = _extract_links(home_html, base_url)
        relevant_links = [l for l in links if _is_relevant(l) and _normalize(l) not in visited]

        # 3. Crawl relevant pages up to max_pages
        for link in relevant_links[:max_pages]:
            norm = _normalize(link)
            if norm in visited:
                continue
            visited.add(norm)
            html = await _fetch(client, link)
            if html:
                text = _extract_text(html)
                if text.strip():
                    pages_content[link] = text

    return pages_content


async def _fetch(client, url: str) -> str | None:
    try:
        resp = await client.get(url)
        if resp.status_code == 200 and "text/html" in resp.headers.get("content-type", ""):
            return resp.text
    except Exception:
        return None
    return None


def _extract_links(html: str, base_url: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    domain = urlparse(base_url).netloc
    links = []
    for a in soup.find_all("a", href=True):
        href = urljoin(base_url, a.get("href", ""))
        if urlparse(href).netloc == domain:  # same-domain only
            links.append(href.split("#")[0])
    return list(dict.fromkeys(links))  # dedupe, preserve order


def _is_relevant(url: str) -> bool:
    lower = url.lower()
    if any(skip in lower for skip in SKIP_KEYWORDS):
        return False
    return any(kw in lower for kw in TARGET_KEYWORDS) or url.rstrip("/").count("/") <= 3


def _normalize(url: str) -> str:
    return url.rstrip("/").lower()


def _extract_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "noscript", "header"]):
        tag.decompose()
    text = soup.get_text(separator=" ", strip=True)
    return " ".join(text.split())[:6000]  # cap length per page to control token usage
