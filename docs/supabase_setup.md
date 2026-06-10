# Supabase Setup

This project can use Supabase as its hosted Postgres database.

## 1. Create A Supabase Project

1. Go to Supabase and create a new project.
2. Save your database password somewhere safe.
3. Wait for the project to finish provisioning.

## 2. Copy The Database URL

In the Supabase dashboard:

1. Open your project.
2. Go to **Connect**.
3. Copy a Postgres connection string.

For local Streamlit development, use the direct or session-style connection string when available.

For serverless jobs, edge functions, or many short n8n executions, use the transaction pooler string. Transaction pooling is good for many short-lived connections, but it does not support prepared statements, so avoid client settings that force prepared statements.

## 3. Configure `.env.local`

Create or update `.env.local`:

```bash
DATABASE_URL="postgresql+psycopg2://postgres:[YOUR-PASSWORD]@[YOUR-HOST]:5432/postgres"
ANTHROPIC_API_KEY="your_anthropic_api_key"
ANTHROPIC_MODEL="claude-haiku-4-5"
```

Keep `.env.local` private. It is intentionally ignored by Git.

## 4. Check The Connection

Run:

```bash
python scripts/check_supabase.py
```

This checks that SQLAlchemy can connect to the configured database and lists existing public tables.

## 5. Create Tables

Run:

```bash
python database.py
```

Only use this when you intentionally want to drop and recreate tables:

```bash
python database.py --reset
```

## 6. Load Reference Data

Load offices and managers:

```bash
python load.py
```

Optionally load sample tickets too:

```bash
python load.py --include-tickets
```

## 7. Run The App

```bash
streamlit run app.py
```

## 8. Use Supabase With n8n

n8n can write to the same Supabase Postgres database.

Suggested flow:

```text
Webhook -> Normalize Payload -> Claude Haiku Classification -> Supabase/Postgres Insert -> Respond -> Notify Team
```

Use:

```text
integrations/n8n/ticket-routing-workflow.example.json
```

In n8n:

1. Import the workflow JSON.
2. Add Anthropic HTTP header credentials.
3. Add Postgres credentials using your Supabase connection details.
4. Test the Webhook node with a sample ticket payload.
5. Confirm the ticket appears in Supabase.
6. Run the Streamlit app and process/reroute the ticket.

Example webhook payload:

```json
{
  "client_guid": "demo-client-001",
  "description": "Customer cannot complete an order in the mobile app.",
  "segment": "VIP",
  "city": "Алматы",
  "attachment": "order_error.png"
}
```

## Recommended Portfolio Explanation

The technical story is:

- Supabase stores operational workflow state.
- Streamlit gives operators a dashboard.
- Claude Haiku performs fast AI enrichment.
- Python routing logic assigns work.
- n8n connects external forms, CRMs, inboxes, and notifications.
