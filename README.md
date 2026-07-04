# Relu Research Assistant

> **Note to Evaluators (Live Demo):** This application is deployed on a free-tier hosting service (Render). **If the site hasn't been visited in 15 minutes, the server goes to sleep. The first time you load the page or run a search, it may take 30–50 seconds to wake up.** Please be patient on the initial load! After waking up, it runs at normal speeds.

An AI-powered Company Research Assistant that enables users to research any company by providing either the company name or its website URL. The application automatically gathers information from the company’s website, analyzes the collected information using AI, identifies potential competitors, and generates a professional downloadable PDF report.

## Tech Stack
- **Backend**: FastAPI (Python)
- **Frontend**: HTML5, CSS3, Vanilla JS
- **AI Processing**: OpenRouter (LLM agnostic)
- **Web Search**: Serper.dev
- **PDF Generation**: ReportLab
- **Website Crawling**: httpx + BeautifulSoup4

## Architecture Workflow
1. User enters a company name or website URL into the chat interface.
2. Search via Serper.dev to identify the official website (if a name was provided).
3. The custom crawler uses `httpx` and `BeautifulSoup4` to discover and scrape content from key pages (Home, About, Products, Pricing).
4. Extracted text is fed to OpenRouter (using models like `gpt-4o-mini` or `claude-3.5-haiku`) to generate a structured JSON business profile.
5. A secondary Serper.dev query finds top industry competitors and alternative solutions.
6. The combined report is rendered in the chat UI.
7. Users can download a professional PDF report rendered dynamically via ReportLab.
8. (Bonus) The report and PDF can be shared instantly to a configured Discord channel via REST API.

## Setup Instructions

### 1. Local Development
```bash
# Clone or navigate to the directory
cd relu-research-assistant

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
```

### 2. Environment Variables (`.env`)
You must fill out the following environment variables in your `.env` file:

| Variable | Required | Description |
|----------|----------|-------------|
| `SERPER_API_KEY` | Yes | API key from serper.dev for web searching |
| `OPENROUTER_API_KEY` | Yes | API key from openrouter.ai for AI generations |
| `DEFAULT_AI_MODEL` | No | Default model slug (e.g., `openai/gpt-4o-mini`). Defaults to `openai/gpt-4o-mini` |
| `PORT` | No | Port for the web server to run on. Defaults to `8000` |

### 3. Running the Server
```bash
python run.py
# The app will be available at http://localhost:8000
```

## Discord Integration (Bonus Feature)
The Discord integration allows you to instantly send the final PDF report to a Discord channel.
1. Create a Discord Bot on the [Discord Developer Portal](https://discord.com/developers/applications).
2. Give the bot the `Send Messages` and `Attach Files` permissions.
3. Invite the bot to your server.
4. Copy your **Bot Token** and the **Channel ID** of the channel you want to send reports to.
5. In the Research Assistant Web UI, open the Settings Sidebar and enter the Token and Channel ID, along with your Applicant Name and Email. Click "Save Config".
6. When a report finishes generating, click "Share to Discord".

## Deployment Instructions (Render or Railway)
This application is designed to be deployed on platforms like **Render** or **Railway** (Vercel is not recommended due to serverless timeouts for long-running AI tasks).

1. Push this repository to GitHub.
2. Connect the repository to your Render/Railway dashboard.
3. **Important for Render**: We switched to `reportlab` for PDF generation, so you do NOT need to install heavy system libraries like `pango` or `cairo`. It is pure Python and deploys instantly!
4. Add the `SERPER_API_KEY` and `OPENROUTER_API_KEY` to the environment variables section of your hosting provider.
5. Deploy!

## Known Limitations
- **Static HTML Crawling**: The internal crawler uses `httpx` and `BeautifulSoup4`. It does not execute JavaScript. If a target company's website is a pure Single Page Application (SPA) without server-side rendering, the extracted content may be limited.
- **In-Memory Discord Storage**: As per the "No permanent database required" spec, Discord configuration settings are stored in memory. They will reset if the FastAPI server restarts.
