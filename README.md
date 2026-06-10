# Intelligent CRM Routing
**Built for the Datasaur Hackathon**

Streamlit app for CRM ticket ingestion, AI classification, manager routing, and result export.

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
OPENAI_API_KEY="your_api_key"
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

## Verification

```bash
python -m py_compile app.py main.py router.py database.py load.py config.py
python -m unittest discover
```
