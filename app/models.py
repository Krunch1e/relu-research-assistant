from pydantic import BaseModel
from typing import List, Optional

class ResearchRequest(BaseModel):
    input: str
    model: str = "openai/gpt-4o-mini"

class Competitor(BaseModel):
    name: str = "Unknown"
    website: str = "#"

class CompanyProfile(BaseModel):
    company_name: str = "Unknown Company"
    website: str = ""
    phone: Optional[str] = None
    address: Optional[str] = None
    products_services: List[str] = []
    pain_points: List[str] = []
    summary: str = "No summary generated."
    competitors: List[Competitor] = []

class DiscordConfigRequest(BaseModel):
    bot_token: str
    channel_id: str

class DiscordSendRequest(BaseModel):
    applicant_name: str
    applicant_email: str
    report: CompanyProfile
