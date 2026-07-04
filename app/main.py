from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
from urllib.parse import urlparse

from app.models import ResearchRequest, DiscordConfigRequest, DiscordSendRequest, CompanyProfile
from app.config import settings
from app.search import find_official_website
from app.crawler import crawl_site
from app.ai import generate_company_profile
from app.competitors import find_competitors
from app.pdf_report import generate_pdf
from app.discord_bot import send_report_to_discord

app = FastAPI(title="Relu Research Assistant")

# Create directories if they don't exist
os.makedirs("app/static", exist_ok=True)
os.makedirs("app/templates", exist_ok=True)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.get("/")
async def get_index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.post("/api/research", response_model=CompanyProfile)
async def research_company(req: ResearchRequest):
    input_text = req.input.strip()
    model = req.model
    
    # 1. Determine if URL or Name
    is_url = input_text.startswith("http://") or input_text.startswith("https://")
    
    if is_url:
        website_url = input_text
        # Optional: guess company name from URL domain
        domain = urlparse(website_url).netloc.replace("www.", "")
        company_name_hint = domain.split(".")[0].capitalize()
    else:
        # Search for official website
        company_name_hint = input_text
        website_url = await find_official_website(input_text)
        if not website_url:
            raise HTTPException(status_code=404, detail="Could not find an official website for this company.")
            
    # 2. Crawl the website
    pages_content = await crawl_site(website_url, max_pages=8)
    
    # Combine content for AI
    combined_content = ""
    if pages_content:
        for url, text in pages_content.items():
            combined_content += f"\n--- Page: {url} ---\n{text}\n"
    else:
        combined_content = f"Could not crawl website {website_url}. Please rely on your pre-trained knowledge to generate the profile."
        
    # 3. Generate Profile using OpenRouter
    try:
        profile_data = await generate_company_profile(combined_content, model)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {e}")
        
    # Ensure missing fields don't crash
    if "company_name" not in profile_data or not profile_data["company_name"]:
        profile_data["company_name"] = company_name_hint
    profile_data["website"] = website_url
        
    # 4. Find Competitors (using the AI summary as context for accuracy)
    industry_hint = profile_data.get("summary", "software/tech/business")[:150]
    competitors = await find_competitors(profile_data["company_name"], industry_hint, model)
    profile_data["competitors"] = competitors
    
    return CompanyProfile(**profile_data)

@app.post("/api/generate-pdf")
async def create_pdf(report: CompanyProfile):
    try:
        pdf_bytes = generate_pdf(report.model_dump())
        # Sanitize filename for HTTP headers (which only support latin-1 and NO newlines)
        import re
        safe_filename = re.sub(r'[^a-zA-Z0-9_\-]', '_', report.company_name)
        if not safe_filename or safe_filename.strip('_') == '':
            safe_filename = "Company"
            
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={safe_filename}_Report.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {e}")

@app.post("/api/discord/configure")
async def configure_discord(req: DiscordConfigRequest):
    settings.discord_bot_token = req.bot_token
    settings.discord_channel_id = req.channel_id
    return {"status": "success", "message": "Discord configured successfully (in-memory)."}

@app.post("/api/discord/send")
async def send_to_discord(req: DiscordSendRequest):
    if not settings.discord_bot_token or not settings.discord_channel_id:
        raise HTTPException(status_code=400, detail="Discord bot token and channel ID not configured.")
        
    try:
        # Re-generate PDF just for sending
        pdf_bytes = generate_pdf(req.report.model_dump())
        
        success = await send_report_to_discord(
            bot_token=settings.discord_bot_token,
            channel_id=settings.discord_channel_id,
            applicant_name=req.applicant_name,
            applicant_email=req.applicant_email,
            company_name=req.report.company_name,
            company_website=req.report.website,
            pdf_bytes=pdf_bytes
        )
        
        if success:
            return {"status": "success"}
        else:
            raise HTTPException(status_code=500, detail="Failed to send message to Discord API.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Discord integration failed: {e}")

@app.get("/api/models")
async def get_models():
    return [
        {"id": "openai/gpt-4o-mini", "name": "GPT-4o Mini (Fast & Cheap)"},
        {"id": "anthropic/claude-3-haiku", "name": "Claude 3 Haiku"},
        {"id": "meta-llama/llama-3.1-8b-instruct", "name": "Llama 3.1 8B"}
    ]
