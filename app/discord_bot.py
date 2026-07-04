import httpx

DISCORD_API = "https://discord.com/api/v10"

async def send_report_to_discord(bot_token: str, channel_id: str,
                                 applicant_name: str, applicant_email: str,
                                 company_name: str, company_website: str,
                                 pdf_bytes: bytes) -> bool:
    url = f"{DISCORD_API}/channels/{channel_id}/messages"
    headers = {"Authorization": f"Bot {bot_token}"}
    embed_text = (
        f"**New Research Submission**\n"
        f"Applicant: {applicant_name} ({applicant_email})\n"
        f"Company: {company_name}\n"
        f"Website: {company_website}"
    )
    files = {"file": ("report.pdf", pdf_bytes, "application/pdf")}
    data = {"content": embed_text}
    
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(url, headers=headers, data=data, files=files)
            if resp.status_code not in (200, 201):
                print(f"Discord API Error: {resp.status_code} {resp.text}")
            return resp.status_code in (200, 201)
    except Exception as e:
        print(f"Failed to send to discord: {e}")
        return False
