# Intelligent CRM Routing
**Built for the Datasaur Hackathon, but later adapted as a fun project**

Streamlit app for CRM ticket ingestion, AI classification, manager routing, operational dashboards, and result export.

This repo also includes neutral integration blueprints that show how the workflow can connect to automation tools such as n8n, Make/Zapier, Airtable, Retool, and Supabase-style stacks.

## How to Run Locally

**1. Clone the repository**
```bash
git clone https://github.com/i-oeng/datasaur_fire.git
cd datasaur_fire
```
**2. Set up the virtual environment & install dependencies**

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
```

**3. Add your environment variables** 

Copy `.env.example` to `.env.local` and add your local values.

```bash
DATABASE_URL="your_database_url"
ANTHROPIC_API_KEY="your_api_key"
ANTHROPIC_MODEL="claude-haiku-4-5"
```

**4. Initialize and load reference data**

```bash
python database.py
python load.py
```

Add the sample tickets too with `python load.py --include-tickets`, or upload tickets from the app.

Use `python database.py --reset` only when you intentionally want to drop and recreate all tables.

**5. Run**
```bash
streamlit run app.py
```


## Usage Guide 
1. Upload Data
2. Review raw data
3. Launch AI
4. Export results 

## Technical Showcase

- Streamlit internal dashboard for operators
- Anthropic Claude structured extraction and summarization
- SQLAlchemy/Postgres-backed workflow state
- Business-rule routing with skills, language, geography, VIP status, and workload balancing
- Attachment-aware document/screenshot processing path
- n8n workflow blueprint for webhook-based CRM automation
- Portfolio talking points for presenting the project without rebranding it for a specific company

See:

- `integrations/README.md`
- `integrations/n8n/ticket-routing-workflow.example.json`
- `docs/portfolio_talking_points.md`
- `docs/model_n8n_supabase_guide.md`
- `docs/supabase_setup.md`

## Verification

```bash
python -m py_compile app.py main.py router.py database.py load.py config.py scripts/check_supabase.py
python -m unittest discover
```
