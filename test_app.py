import asyncio
from app.search import find_official_website
from app.crawler import crawl_site
from app.ai import generate_company_profile
from app.competitors import find_competitors

async def main():
    try:
        print("Testing search...")
        url = await find_official_website("Stripe")
        print(f"URL: {url}")
        
        print("Testing crawler...")
        pages = await crawl_site(url, max_pages=2)
        print(f"Crawled {len(pages)} pages")
        
        content = list(pages.values())[0] if pages else ""
        
        print("Testing AI...")
        profile = await generate_company_profile(content, "openai/gpt-4o-mini")
        print("Profile generated")
            
        print("Testing competitors...")
        comps = await find_competitors("Stripe", "tech", "openai/gpt-4o-mini")
        print(f"Competitors: {len(comps)}")
    except Exception as e:
        import traceback
        traceback.print_exc()

asyncio.run(main())
